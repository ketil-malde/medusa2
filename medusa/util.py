# File hash from hashlib
import hashlib
import mmap

def get_hash(fhandle):
    # is this effcient?  newer hashlib supports file_digest, probably better
    with mmap.mmap(fhandle.fileno(), length=0, access=mmap.ACCESS_READ) as fm:
        return hashlib.sha256(fm).hexdigest()

def hashstring(string):
    return hashlib.sha256(string.encode()).hexdigest()

# Colors for text highlighting
MAGENTA = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
WARN = '\033[93m'  # yellow
FAIL = '\033[91m'  # red
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def error(string, stop=True):
    print(f'{FAIL}Error:{ENDC} {string}')
    if stop: exit(-1)

def warn(string, stop=True):
    print(f'{WARN}Warning:{ENDC} {string}')
    if stop: exit(-1)
