python3 << EOF

import medusa.datasets as md

D = md.Datasets('/tmp/medusa')
h = D.insert('examples/flowcam1')
D.delete(h)
print('Listing the log:')
D.list()
print('Exporting dataset:')
D.export(h, 'tmp_export')
EOF

tree tmp_export
rm -rf tmp_export

