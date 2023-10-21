from lxml import etree
from os.path import dirname

def validate(manifest):
    libdir = dirname(dirname(__file__))+'/xml/'
    with open(f'{libdir}/manifest.rng', 'r') as f:
        schema = etree.RelaxNG(etree.parse(f))
    with open(manifest, 'r') as f:
        doc = etree.parse(f)
    return schema.validate(doc)
    
