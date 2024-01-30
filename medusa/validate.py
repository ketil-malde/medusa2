from lxml import etree
from os.path import dirname
import rnc2rng
from medusa.util import get_hash, error, warn

def validate_text_plain(fh):
    # check correct utf-8 text
    return True

def validate_csv(fh):
    # check number of fields is constant
    return True

def validate_tiff(fh):
    # verify image
    return True

# Table of content validation functions
validate_file = {
    'text/plain' : validate_text_plain,
    'text/csv'   : validate_csv,
    'image/tiff' : validate_tiff
}

def validate(dataset, quick=False, datatype=None):
    '''Validate a dataset.  Set quick to stop at first error.'''
    status = True
    libdir = dirname(dirname(__file__))+'/xml/'
    rngstr = rnc2rng.dumps(rnc2rng.load(f'{libdir}/manifest.rnc')).encode()
    schema = etree.RelaxNG(etree.fromstring(rngstr))
    doc = etree.parse(f'{dataset}/manifest.xml')
    if not schema.validate(doc):
        print(f'Metadata file "{dataset}/manifest.xml": validation failed')
        print(schema.error_log)
        status = False
        if quick: return False

    # TODO: data-specific validation (e.g. flowcam)

    # Check all declared objects
    for obj in doc.iter('object'):
        fname = f'{dataset}/{obj.attrib["path"]}'
        ftype = obj.attrib['mimetype']
        fhash = obj.attrib['sha256']
        with open(fname, 'rb') as fh:
            h = get_hash(fh)
            if h != fhash:
                print('ERROR: checksum mismatch for {fname}, got {h}, wanted {fhash}!')
                status = False
                if quick: return False
            else:
                print(f'   "{fname}" - checksum OK')

            # check file contents of fh
            if ftype in validate_file:
                if not validate_file[ftype](fh):
                    error(f'File format validation failed for {fname} as {ftype}.', stop=quick)
                    status = False
                    if quick: return False
            else:
                warn(f'Unknown file type "{ftype}" for file "{fname}" - ignoring.')

    # TODO: Check all files present are declared (or warn)

    return status
    
