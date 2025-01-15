from medusa.util import error

import json
from datetime import datetime, UTC
from sshkey_tools.keys import RsaPrivateKey, PublicKey
from sshkey_tools.exceptions import InvalidSignatureException
from os import path

class Ledger:
    def __init__(self, config, store):
        # maybe read cache?  Add initial key if new ledger
        self.ssh_key = RsaPrivateKey.from_file(path.expanduser(config['rsakey']))
        self.username = config['username']
        self.userid = config['userid']
        self._store = store
        self._users = {}
        # todo: use local cache
        for d in reversed(self.list(check=False)):
            if d['Prev'] != 'None':
                self.verify(d)
            if 'AddUser' in d.keys():
                self._users[d['AddUser']] = {'Key': d['Key'], 'Name' : d['Name']}
        print('Initialized ledger.')

    def log_insert(self, new_hash):
        '''Register a new dataset'''
        self.register({'Insert': new_hash})

    def log_delete(self, del_hash):
        '''Register deletion of a dataset'''
        self.register({'Delete': del_hash})

    def log_adduser(self, userid, username, pubkey):
        '''Register a new user'''
        if userid in self._users:
            error(f'User {userid} already exists as {self._users[userid]["Name"]}.')
        # check that key is unique, too?
        self.register({'AddUser': userid, 'Name': username, 'Key': pubkey})

    def log_deluser(self, user):
        '''Revoke a user'''
        # Check that submitting user has rights
        self.register({'DelUser': user})

    def register(self, msgdict):
        '''Add log message, replace HEAD'''
        prevhash = self._store.gethead()
        msgdict['Prev'] = prevhash
        msgdict['Date'] = str(datetime.now(UTC))
        msgdict = self.sign(msgdict)
        myhash = self._store.puts(json.dumps(msgdict).encode())
        self._store.sethead(myhash)

    def list(self, check=True):
        '''Traverse the log and return the datasets'''
        # should be an Iterator?
        res = []
        cur = self._store.gethead()
        if cur == 'None': cur = None
        while cur is not None:
            msg = self._store.gets(cur)
            log_entry = json.loads(msg)
            if check and not self.verify(log_entry):
                error('Incorrect signature!')
            # else:
            #    print('Signature OK')
            res.append(log_entry)
            cur = log_entry['Prev']
            if cur == 'None': cur = None
        return res

    # Signatures using SSH?
    # better -> https://pypi.org/project/sshkey-tools/
    # https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb#file-1_sign-py-L19

    def sign(self, msg):
        msg['User'] = self.userid
        msg['Signature'] = self.ssh_key.sign(json.dumps(msg).encode()).hex()
        return msg

    def verify(self, msg):
        # warning: messes with the message!
        uid = msg['User']
        sig = msg.pop('Signature')
        try:
            pkey = PublicKey.from_string(self._users[uid]['Key'])
            pkey.verify(json.dumps(msg).encode(), bytes.fromhex(sig))
        except InvalidSignatureException:
            return False
        return True
