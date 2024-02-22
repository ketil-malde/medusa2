python3 <<EOF

import medusa.storage as ms

S = ms.FileStorage('/tmp/mdz')

S.put('test_repo.sh')
h=S.put('test_repo.sh')
S.get(h, 'tmp_link')

EOF
tree /tmp/mdz
ls -l tmp_link
