python3 << EOF

import medusa.datasets as md
import medusa.storage as ms

D = md.Datasets(ms.FileStorage('/tmp/medusa'))
h = D.insert('examples/flowcam1')
D.export(h, 'tmp_export')
EOF

tree tmp_export
rm -rf tmp_export

