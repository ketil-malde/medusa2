import medusa.util as util
from medusa.util import error

from tempfile import NamedTemporaryFile
import os
import pysftp as sftp

def repo_parse(repo):
    # Format: [ketil@]host.name:directory/path
    host, path = repo.split(':')
    userhost = host.split('@')
    if len(userhost) == 2:
        return userhost[0], userhost[1], path
    else:
        return None, host, path

class SftpStorage:
    '''Implements a storage for objects using SFTP'''

    def __init__(self, config, create=False):
        user, host, directory = repo_parse(config['repository'])
        self._conn = sftp.Connection(host, username=user)

        if create:
            assert not self._conn.exists(directory), error(f'Cannot initialize SFT storage, {host}:{directory} exists already.')
            self._conn.makedirs(directory)
            self._conn.chdir(directory)

            with NamedTemporaryFile(delete=False) as f:
                f.write(b'None')
            self._conn.put(f.name, 'HEAD')
            os.unlink(f.name)

            print('New file storage intialized: ', config['repository'])
        else:
            assert self._conn.exists(directory), error(f'Repository {directory} does not exist on {host}.')
            self._conn.chdir(directory)
            assert self._conn.exists('HEAD'), error('Repository found, but no HEAD')
            print('Existing file storage initialized: ', config['repository'])

    def hash2dir(self, fhash):
        '''Directory prefix for storing hashes'''
        return (fhash[:3], fhash[3:6])

    def exists(self, fhash):
        fname = os.path.join(self.hash2dir(fhash)[0], self.hash2dir(fhash)[1], fhash)
        return self._conn.exists(fname)

    def put(self, filename, verify_exists=True):
        with open(filename, 'rb') as fh:
            fhash = util.get_hash(fh)
        dname = os.path.join(self.hash2dir(fhash)[0], self.hash2dir(fhash)[1])
        fname = os.path.join(dname, fhash)
        if not self._conn.exists(dname):
            self._conn.makedirs(dname)
        if not self._conn.exists(fname):
            self._conn.put(filename, fname)
        else:
            print(f'Skipping "{filename}", object already exists as {fhash}.')
        return fhash

    def get(self, fhash, fname=None, mode=None):
        '''Get object associated with fhash as specified by mode'''
        objname = os.path.join(self.hash2dir(fhash)[0], self.hash2dir(fhash)[1], fhash)
        if not fname: fname = fhash
        if not self._conn.exists(objname):
            print(f'Object not found: {fhash}')
        else:
            self._conn.get(objname, fname)

    def puts(self, mystring):
        '''Put a string as an object'''
        fhash = util.hashstring(mystring)
        dname = os.path.join(self.hash2dir(fhash)[0], self.hash2dir(fhash)[1])
        fname = os.path.join(dname, fhash)
        if not self._conn.exists(dname):
            self._conn.makedirs(dname)
        if not self._conn.exists(fname):
            with NamedTemporaryFile(delete=False) as f:
                f.write(mystring.encode())
            self._conn.put(f.name, fname)
            os.unlink(f.name)

        else:
            print('Object already exists')
        return fhash

    def gets(self, myhash):
        '''Get an object as a string'''
        objname = os.path.join(self.hash2dir(myhash)[0], self.hash2dir(myhash)[1], myhash)
        if not self._conn.exists(objname):
            print(f'Object not found: {myhash}')
            return None
        else:
            tf = NamedTemporaryFile()
            self._conn.get(objname, tf.name)
            with open(tf.name) as f:
                mystring = f.read()
            tf.close()
            return mystring

    def gethead(self):
        assert self._conn.exists('HEAD'), 'oopsie? No head?'
        head = NamedTemporaryFile()
        self._conn.get('HEAD', head.name)
        with open(head.name, 'r') as f:
            s = f.readline()
        head.close()
        return s

    def sethead(self, myhash):
        with NamedTemporaryFile(delete=False) as f:
            f.write(f'{myhash}'.encode())
        self._conn.put(f.name, 'HEAD')
        os.unlink(f.name)
