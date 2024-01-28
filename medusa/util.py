# File hash from hashlib
import hashlib
import mmap

def get_hash(fhandle):
    # is this effcient?  newer hashlib supports file_digest, probably better
    with mmap.mmap(fhandle.fileno(), length=0, access=mmap.ACCESS_READ) as fm:
        return hashlib.sha256(fm).hexdigest()

def error(string):
    print(f'Error: {string}')
    exit(-1)
