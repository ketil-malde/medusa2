from lxml import etree
from os.path import dirname
import mmap
import hashlib

def validate_text_plain(fh):
    # check correct utf-8 text
    pass

def validate_csv(fh):
    # check number of fields is constant
    pass

# Table of content validation functions
validate_type = {
    'text/plain' : validate_text_plain,
    'text/csv'   : validate_csv
}

def validate(dataset):
    status = None
    libdir = dirname(dirname(__file__))+'/xml/'
    with open(f'{libdir}/manifest.rng', 'r') as f:
        schema = etree.RelaxNG(etree.parse(f))
    with open(f'{dataset }/manifest.xml', 'r') as f:
        doc = etree.parse(f)
    status = schema.validate(doc)

    # data-specific validation (e.g. flowcam)

    # madvise(mmap.MADV_SEQUENTIAL)
    # Check objects
    for obj in doc.iter('object'):
        fname = f'{dataset}/{obj.attrib["path"]}'
        ftype = obj.attrib['mimetype']
        fhash = obj.attrib['sha1']
        with open(fname, 'rb') as fh:
            # is this effcient?  newer hashlib supports file_digest, probably better
            with mmap.mmap(fh.fileno(), length=0, access=mmap.ACCESS_READ) as fm:
                h = hashlib.sha1(fm).hexdigest()
                if h != fhash:
                    print('ERROR: checksum mismatch for {fname}, got {h}, wanted {fhash}!')
                    status = False
                else:
                    print(f'   "{fname}" - checksum OK')

                # check file contents of fh/fm
                validate_type[ftype](fm)

    return status
    
