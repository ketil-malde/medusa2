import requests
from requests import HTTPError, ConnectionError, Timeout, TooManyRedirects, RequestException
from medusa.util import error

def connection(func):
    '''Handle errors with requests'''
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as e:
            error(f"HTTP Error: {e}")
        except ConnectionError as e:
            error(f"Connection Error: {e}")
        except Timeout as e:
            error(f"Timeout Error: {e}")
        except TooManyRedirects as e:
            error(f"Too Many Redirects Error: {e}")
        except RequestException as e:
            error(f"An unexpected Requests error occurred: {e}")
        except Exception as e:
            error(f"An unexpected error occurred: {e}")
    return wrapper


class HttpStorage:
    '''Implements Storage as a REST service'''

    def __init__(self, config):  # don't think we can create via HTTP?
        self._repo = config['repository']

    @connection
    def exists(self, fhash):
        r = requests.head(self._repo + 'get/' + fhash)
        return r.status_code == 200

    @connection
    def put(self, filename, verify_exists=True):
        '''Put an object in the repository, returning its hash'''
        with open(filename, 'rb') as payload:
            r = requests.post(self._repo + 'put/', data=payload)
        return r.content.decode()

    @connection
    def expand_prefix(self, fhash):
        return [fhash]

    @connection
    def get(self, fhash, fname):
        '''Get object associated with fhash'''
        r = requests.get(self._repo + 'get/' + fhash)
        if fname is None: fname = fhash
        with open(fname, 'wb') as f: f.write(r.content)

    @connection
    def puts(self, mystring):
        '''Put a string as an object'''
        r = requests.post(self._repo + 'put/', data=mystring)
        return r.content.decode()

    @connection
    def gets(self, myhash):
        assert isinstance(myhash, str)
        '''Get an object as a (byte?)string'''
        r = requests.get(self._repo + 'get/' + myhash)
        # check for error
        return r.content

    @connection
    def gethead(self):
        r = requests.get(self._repo)
        return r.content.decode()  # returns a str

    @connection
    def sethead(self, myhash):
        assert isinstance(myhash, str)
        requests.post(self._repo, myhash)
