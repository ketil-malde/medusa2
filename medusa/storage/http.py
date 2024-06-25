import requests

class HttpStorage:
    '''Implements Storage as a REST service'''

    def __init__(self, config):  # don't think we can create via HTTP?
        self._repo = config['repository']

    def exists(self, fhash):
        r = requests.head(self._repo + fhash)
        return r.status_code == 200

    def put(self, filename, verify_exists=True):
        '''Put an object in the repository, returning its hash'''
        with open(filename, 'rb') as payload:
            r = requests.post(self._repo, data=payload)
        return r.content.decode()

    def get(self, fhash, fname):
        '''Get object associated with fhash'''
        r = requests.get(self._repo + fhash)
        if fname is None: fname = fhash
        with open(fname, 'wb') as f: f.write(r.content)

    def puts(self, mystring):
        '''Put a string as an object'''
        r = requests.post(self._repo, data=mystring)
        return r.content.decode()

    def gets(self, myhash):
        '''Get an object as a (byte?)string'''
        r = requests.get(self._repo + myhash)
        # check for error
        return r.content

    def gethead(self):
        r = requests.get(self._repo)
        return r.content.decode()

    def sethead(self, myhash):
        requests.post(self._repo + 'HEAD', myhash)
