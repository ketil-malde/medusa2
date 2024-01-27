python3 <<EOF

import medusa.storage as ms

S = ms.FileStorage('/tmp/mdz')

S.put('test.sh')
h=S.put('test.sh')
S.get(h, 'tmp_link')

EOF
tree /tmp/mdz
ls -l tmp_link
