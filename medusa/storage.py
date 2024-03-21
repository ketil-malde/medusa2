import medusa.util as util
from os import path, makedirs, symlink
import shutil

# Should this be a (base) class?
def mkstorage(repo):
    '''Selects storage based on specifier'''
    # repo starts with "HTTP" or "HTTPS"
    # repo starts with "IPFS"
    # otherwise
    return FileStorage(repo)

class FileStorage:
    '''Implements a file-based storage for objects'''

    def __init__(self, repo):
        print('File storage intialized: ', repo)
        self._repo = repo

    def hash2dir(self, fhash):
        '''Directory prefix for storing hashes'''
        return(fhash[:3], fhash[3:6])

    def exists(self, fhash):
        fname = path.join(self._repo, self.hash2dir(fhash)[0], self.hash2dir(fhash)[1], fhash)
        return path.exists(fname)

    def put(self, filename, verify_exists=True):
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
            print('Object not found')
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
            print('Object not found')
            return None
        else:
            with open(objname, 'r') as f:
                mystring = f.read()
            return mystring

class IPFSStorage():
    pass
