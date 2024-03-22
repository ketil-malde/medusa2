import json

class Ledger:
    def __init__(self, store):
        '''maybe read cache?'''
        print('Initialized ledger.')
        self._store = store

    def log_insert(self, new_hash):
        '''Register a new dataset'''
        self.register({'Insert': new_hash})

    def log_delete(self, del_hash):
        '''Register deletion of a dataset'''
        self.register({'Delete': del_hash})

    def register(self, msgdict):
        '''Add log message, replace HEAD'''
        prevhash = self._store.gethead()
        msgdict['Prev'] = prevhash
        myhash = self._store.puts(json.dumps(msgdict))
        self._store.sethead(myhash)
    
    def list(self):
        '''Traverse the log and return the datasets'''
        cur = self._store.gethead()
        while cur is not None:
            log_entry = json.loads(self._store.gets(cur))
            print(log_entry)
            cur = log_entry['Prev']
            if cur == 'None': cur = None
