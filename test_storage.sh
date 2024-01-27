python3 << EOF

import medusa.datasets as md
import medusa.storage as ms

D = md.Datasets(ms.FileStorage('/tmp/medusa'))
D.insert('examples/flowcam1')

EOF
tree -d /tmp/medusa
