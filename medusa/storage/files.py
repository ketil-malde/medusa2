import medusa.util as util
from medusa.util import error

from os import path, makedirs, symlink
import shutil

class FileStorage:
    '''Implements a file-based storage for objects'''

    def __init__(self, config, create=False):
        repopath = config['repository']
        head = path.join(repopath, 'HEAD')

        if create:
            assert not path.exists(repopath), error(f'Cannot create {repopath}, it exists already.')
            makedirs(config['repository'], exist_ok=True)
            with open(head, 'w') as f:
                f.write('None')
            print('New file storage intialized: ', repopath)
        else:
            assert path.exists(repopath), error(f'Repository {repopath} does not exist.')
            assert path.exists(head), error('Repository found, but no HEAD')
            print('Existing file storage initialized: ', repopath)

        self._repo = config['repository']

    def hash2dir(self, fhash):
        '''Directory prefix for storing hashes'''
        return (fhash[:3], fhash[3:6])

    def exists(self, fhash):
        fname = path.join(self._repo, self.hash2dir(fhash)[0], self.hash2dir(fhash)[1], fhash)
        return path.exists(fname)

    def put(self, filename, verify_exists=True):
        '''Put an object in the repository, returning its hash'''
        with open(filename, 'rb') as fh:
            fhash = util.get_hash(fh)
        dname = path.join(self._repo, self.hash2dir(fhash)[0], self.hash2dir(fhash)[1])
        fname = path.join(dname, fhash)
        if not path.exists(dname):
            makedirs(dname, exist_ok=True)
        if not path.exists(fname):
            shutil.copy(filename, fname)
        else:
            print(f'Skipping "{filename}", object already exists as {fhash}.')
        return fhash

    def get(self, fhash, fname=None, mode=None):
        '''Get object associated with fhash as specified by mode'''
        objname = path.join(self._repo, self.hash2dir(fhash)[0], self.hash2dir(fhash)[1], fhash)
        if not fname: fname = fhash
        if not path.exists(objname):
            print(f'Object not found: {fhash}')
        elif mode == 'copy':
            shutil.copy(objname, fname)
        else:
            symlink(objname, fname)
        pass

    def puts(self, mystring):
        '''Put a string as an object'''
        fhash = util.hashstring(mystring)
        dname = path.join(self._repo, self.hash2dir(fhash)[0], self.hash2dir(fhash)[1])
        fname = path.join(dname, fhash)
        if not path.exists(dname):
            makedirs(dname, exist_ok=True)
        if not path.exists(fname):
            with open(fname, 'w') as f:
                f.write(mystring)
        else:
            print('Object already exists')
        return fhash

    def gets(self, myhash):
        '''Get an object as a string'''
        objname = path.join(self._repo, self.hash2dir(myhash)[0], self.hash2dir(myhash)[1], myhash)
        if not path.exists(objname):
            print(f'Object not found: {myhash}')
            return None
        else:
            with open(objname, 'r') as f:
                mystring = f.read()
            return mystring

    def gethead(self):
        head = path.join(self._repo, 'HEAD')
        assert path.exists(head), f'oopsie? {self._repo}'
        with open(head, 'r') as f:
            s = f.readline()
        return s

    def sethead(self, myhash):
        with open(path.join(self._repo, 'HEAD'), 'w') as f:
            f.write(f'{myhash}')
