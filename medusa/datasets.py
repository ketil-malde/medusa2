# Deal with datasets and storage
# use storage.py to manage storage
# use ledger.py (todo) to manage records
from medusa.validate import validate
from medusa.util import error
from lxml import etree
import os

class Datasets:
    def __init__(self, storage):
        self._store = storage

    def insert(self, dataset):
        # verify metadata file
        if not os.path.exists(dataset):
            error(f'No such directory: {directory}')
        # validate dir
        if not validate(dataset):
            error(f'Validation failed')

        # iterate over all objects and store them
        doc = etree.parse(f'{dataset}/manifest.xml')
        for obj in doc.iter('object'):
            fname = f'{dataset}/{obj.attrib["path"]}'
            fhash = obj.attrib['sha256']
            newhash = self._store.put(fname)
            assert newhash == fhash
        return self._store.put(f'{dataset}/manifest.xml')

    def extract(self, dhash, dname=None):
        # create dir
        # extract metadata file
        # extract all objects
        pass
