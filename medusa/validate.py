from lxml import etree
from os.path import dirname
import mmap
import hashlib
import rnc2rng

def validate_text_plain(fh):
    # check correct utf-8 text
    pass

def validate_csv(fh):
    # check number of fields is constant
    pass

def validate_tiff(fh):
    # verify image
    pass

# Table of content validation functions
validate_type = {
    'text/plain' : validate_text_plain,
    'text/csv'   : validate_csv,
    'image/tiff' : validate_tiff
}

def validate(dataset):
    status = True
    libdir = dirname(dirname(__file__))+'/xml/'
    rngstr = rnc2rng.dumps(rnc2rng.load(f'{libdir}/manifest.rnc')).encode()
    schema = etree.RelaxNG(etree.fromstring(rngstr))
    doc = etree.parse(f'{dataset}/manifest.xml')
    if not schema.validate(doc):
        print(f'Metadata file "{dataset}/manifest.xml": validation failed')
        print(schema.error_log)
        status = False

    # data-specific validation (e.g. flowcam)

    # madvise(mmap.MADV_SEQUENTIAL)
    # Check objects
    for obj in doc.iter('object'):
        fname = f'{dataset}/{obj.attrib["path"]}'
        ftype = obj.attrib['mimetype']
        fhash = obj.attrib['sha256']
        with open(fname, 'rb') as fh:
            # is this effcient?  newer hashlib supports file_digest, probably better
            with mmap.mmap(fh.fileno(), length=0, access=mmap.ACCESS_READ) as fm:
                h = hashlib.sha256(fm).hexdigest()
                if h != fhash:
                    print('ERROR: checksum mismatch for {fname}, got {h}, wanted {fhash}!')
                    status = False
                else:
                    print(f'   "{fname}" - checksum OK')

                # check file contents of fh/fm
                validate_type[ftype](fm)

    return status
    
