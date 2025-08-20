import os
from medusa.util import get_hash
import datetime

def create_template(dirname, name=None, date=None, author=None, description=None, provenance=None):
    info = not name
    if not name:
        name = os.path.basename(dirname)
    if not date:
        date = datetime.date.today().strftime('%Y-%m-%d')
    if not author:
        pass

    objs = []
    for f in os.listdir(dirname):
        if f == 'manifest.xml':
            continue
        try:
            o = {}
            with open(dirname + '/' + f, 'r') as fh:
                o['sha256'] = get_hash(fh)
            o['mimetype'] = 'application/octet-stream'
            o['path'] = f
            objs.append(o)
        except Exception as e:
            print(f'Processing {f} failed: {e}')

    with open(f'{dirname}/manifest.xml', 'w') as f:
        f.write(header(name=name, date=date, author=author, info=info))
        f.write(mkdescription(description))
        f.write(mkprovenance(provenance))
        f.write(objects(objs))
        f.write(footer())

def header(name=None, date=None, author=None, cls=None, info=False):
    myclass = '' if cls is None else f' class="{cls}"'
    hd = f'<manifest name="{name}" created="{date}" author="{author}"{myclass} >\n'

    if info:
        hd += '''  <!-- name is an arbitrary string, dates should be ISO format, person
       is a valid email(?), and class gives hints to the validator on
       what needs to be present -->
'''
    else: print(name, date, author)
    return hd

def mkdescription(desc=None):
    if desc and os.path.exists(desc):
        with open(desc, 'r') as f:
            desctxt = f.read()
        return '  <description>\n' + desctxt + '  </description>\n'
    else: return '''  <description>
    <!-- Just a textual description.  May contain XML elements
         referring to specific types of information (including other
         datasets).  Valid elements are <species>, <person>, <location> etc. -->

    This is a description of the dataset.
  </description>

'''

def mkprovenance(prov=None):
    if prov and os.path.exists(prov):
        with open(prov, 'r') as f:
            provtxt = f.read()
        return '  <provenance>\n' + provtxt + '  </provenance>\n'
    else: return '''  <provenance>
    <!-- Also text, describing the origins of the data, but with a bit
         more structure. E.g. you can use <process name="..." version="..." git-hash="..." />
         or <instrument>....</instrument>.  Automated processing record their actions here. -->

    This is a description of how the data set came to be.
  </provenance>

'''

def obj(obj):
    return f'''    <object sha256="{obj['sha256']}"
            path="{obj['path']}"
            mimetype="{obj['mimetype']}" />
'''

def objects(obj_list):
    nlc = '\n'
    return f'''  <objects>
    <!-- the actual data is listed here -->
    {nlc.join([obj(o) for o in obj_list])}
  </objects>

'''

def footer():
    return '''</manifest>
'''
