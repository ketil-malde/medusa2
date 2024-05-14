# Deal with datasets and storage
# use storage.py to manage storage
# use ledger.py (todo) to manage records
from medusa.ledger import Ledger
from medusa.validate import validate
from medusa.util import error, get_hash
from medusa.storage import mkstorage

from sshkey_tools.keys import RsaPrivateKey
from lxml import etree
import os

# config is a dict which should contain
#   username = Ketil Malde
#   userid   = ketil@malde.org
#   rsakey   = ~/.ssh/id_rsa
#   repository = <location>

def read_ssh_key(keyfile):
    # should probably have a way to only read public key?
    return RsaPrivateKey.from_file(os.path.expanduser(keyfile))

class Datasets:
    def __init__(self, config, create=False):
        print(f'Initializing Dataset: {config}')
        self._store = mkstorage(config, create)
        self._ledger = Ledger(config, self._store)
        self._config = config
        if create:
            ssh_key = read_ssh_key(self._config['rsakey'])
            self.adduser(self._config['userid'], self._config['username'], ssh_key.public_key.to_string())

    def adduser(self, userid, name, key):
        self._ledger.log_adduser(userid, name, key)

    def insert(self, dataset):
        # verify metadata file
        if not os.path.exists(dataset):
            error(f'No such directory: {dataset}.')
        # validate dir
        if not validate(dataset, quick=True):
            error(f'Validation failed for {dataset}.')

        # skip if already exists
        with open(f'{dataset}/manifest.xml', 'r') as fh:
            myhash = get_hash(fh)
        if self._store.exists(myhash):
            print(f'Dataset {dataset} already registered.')
            return myhash

        # iterate over all objects and store them
        doc = etree.parse(f'{dataset}/manifest.xml')
        for obj in doc.iter('object'):
            fname = f'{dataset}/{obj.attrib["path"]}'
            fhash = obj.attrib['sha256']
            newhash = self._store.put(fname)
            assert newhash == fhash

        myhash = self._store.put(f'{dataset}/manifest.xml')
        # fixme: how to deal with multiple inserts of existing datasets?
        self._ledger.log_insert(myhash)
        return myhash

    def export(self, dhash, dname=None):
        if not self._store.exists(dhash):
            error(f'Hash {dhash} not found in repository.')
        else:
            if not dname: dname = dhash
            os.mkdir(dname)
            self._store.get(dhash, f'{dname}/manifest.xml')
            doc = etree.parse(f'{dname}/manifest.xml')
            for obj in doc.iter('object'):
                fname = f'{dname}/{obj.attrib["path"]}'
                fhash = obj.attrib['sha256']
                self._store.get(fhash, fname)
                # todo: make subdirs?
            # todo: mv from dhash to dataset name?

    def delete(self, dhash):
        if not self._store.exists(dhash):
            error(f'Cannot delete nonexistent dataset {dhash}.')
        else:
            self._ledger.log_delete(dhash)

    def list(self):
        '''Process log to list datasets'''
        return self._ledger.list()
