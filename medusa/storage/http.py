import requests
from medusa.util import error

class HttpStorage:
    '''Implements Storage as a REST service'''

    def __init__(self, config):  # don't think we can create via HTTP?
        self._repo = config['repository']

    def exists(self, fhash):
        r = requests.head(self._repo + 'get/' + fhash)
        return r.status_code == 200

    def put(self, filename, verify_exists=True):
        '''Put an object in the repository, returning its hash'''
        with open(filename, 'rb') as payload:
            r = requests.post(self._repo + 'put/', data=payload)
        return r.content.decode()

    def expand_prefix(self, fhash):
        return [fhash]

    def get(self, fhash, fname):
        '''Get object associated with fhash'''
        r = requests.get(self._repo + 'get/' + fhash)
        if fname is None: fname = fhash
        with open(fname, 'wb') as f: f.write(r.content)

    def puts(self, mystring):
        '''Put a string as an object'''
        r = requests.post(self._repo + 'put/', data=mystring)
        return r.content.decode()

    def gets(self, myhash):
        assert isinstance(myhash, str)
        '''Get an object as a (byte?)string'''
        r = requests.get(self._repo + 'get/' + myhash)
        # check for error
        return r.content

    def gethead(self):
        r = requests.get(self._repo)
        return r.content.decode()  # returns a str

    def sethead(self, myhash):
        assert isinstance(myhash, str)
        requests.post(self._repo, myhash)
