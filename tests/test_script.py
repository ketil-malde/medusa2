import medusa.storage as ms
import medusa.datasets as md

config = {'repository': '/tmp/xxxmedusa', 'rsakey': '~/.ssh/id_rsa', 'username': 'Test User', 'userid': 'test@example.com'}

def test_initialize():
    md.Datasets(config, create=True)

def test_storage():
    S = ms.FileStorage(config)
    h = S.put('README.md')
    S.get(h, 'tmp_link')
    # tmp_link should now contain the same contents as test_repo.sh

def test_repo():
    D = md.Datasets(config)
    h = D.insert('examples/flowcam1')
    D.delete(h)
    print('Listing the log:')
    D.list()
    print('Exporting dataset:')
    D.export(h, 'tmp_export')

# Cleanup    
import shutil
import os

def test_cleanup():
    shutil.rmtree(config['repository'])
    shutil.rmtree('tmp_export')
    os.unlink('tmp_link')
