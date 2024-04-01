from medusa.util import error

import json
from datetime import datetime
from sshkey_tools.keys import RsaPrivateKey
from sshkey_tools.exceptions import InvalidSignatureException
from os import path

class Ledger:
    def __init__(self, store):
        # maybe read cache?  Add initial key if new ledger
        self.ssh_key = RsaPrivateKey.from_file(path.expanduser('~/.ssh/id_rsa'))
        self._store = store
        print('Initialized ledger.')

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
        msgdict['Date'] = str(datetime.utcnow())
        msgdict = self.sign(msgdict)
        myhash = self._store.puts(json.dumps(msgdict))
        self._store.sethead(myhash)

    def list(self):
        '''Traverse the log and return the datasets'''
        res = []
        cur = self._store.gethead()
        while cur is not None:
            log_entry = json.loads(self._store.gets(cur))
            if not self.verify(log_entry):
                error('Incorrect signature!')
            else:
                print('Signature OK')
            res.append(log_entry)
            cur = log_entry['Prev']
            if cur == 'None': cur = None
        return res

    # Signatures using SSH?
    # better -> https://pypi.org/project/sshkey-tools/
    # https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb#file-1_sign-py-L19

    def sign(self, msg):
        msg['Signature'] = self.ssh_key.sign(json.dumps(msg).encode()).hex()
        return msg

    def verify(self, msg):
        sig = msg.pop('Signature')
        try:
            self.ssh_key.public_key.verify(json.dumps(msg).encode(), bytes.fromhex(sig))
        except InvalidSignatureException:
            return False
        return True

