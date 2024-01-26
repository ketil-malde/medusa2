# Define MDZREPO - file path, scp directory, or ipfs server
# Maybe make different classes with get/put functions?

import util
import sys
from os import path, makedirs, symlink
import shutil

class FileStorage:
    '''Implements a file-based storage for objects'''

    def __init__(self, repo=None):
        if repo:
            self._repo = repo
        elif 'MDZREPO' in sys.env:
            self._repo = sys.env['MDZREPO']
        # assert repo exists?

    def hash2dir(self, fhash):
        '''Directory prefix for storing hashes'''
        return(fhash[:3], fhash[3:6])

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

class IPFSStorage():
    pass
