from lxml import etree
from os.path import dirname
import mmap
import hashlib

def validate(dataset):
    status = None
    libdir = dirname(dirname(__file__))+'/xml/'
    with open(f'{libdir}/manifest.rng', 'r') as f:
        schema = etree.RelaxNG(etree.parse(f))
    with open(f'{dataset }/manifest.xml', 'r') as f:
        doc = etree.parse(f)
    status = schema.validate(doc)

    # data-specific validation (e.g. flowcam)

    # Check object hashes:
    # madvise(mmap.MADV_SEQUENTIAL)
    for obj in doc.iter('object'):
        fname = f'{dataset}/{obj.attrib["path"]}'
        with open(fname, 'rb') as fh:
            # is this effcient?  newer hashlib supports file_digest, probably better
            with mmap.mmap(fh.fileno(), length=0, access=mmap.ACCESS_READ) as fm:
                h = hashlib.sha1(fm).hexdigest()
                if h != obj.attrib['sha1']:
                    print('ERROR: checksum mismatch for {fname}, got {h}, wanted {obj.attrib["sha1"]}!')
                    status = False
                else:
                    print(f'   "{fname}" - checksum OK')
                # compare sha1.hexdigest() to the stored value
                
    return status
    
