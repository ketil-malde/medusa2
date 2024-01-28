export PYTHONPATH=.

echo '*** VALIDATING ***'
mdz/mdz validate examples/flowcam1

echo; echo '*** IMPORTING ***'
export MDZREPO=/tmp/M
mdz/mdz import examples/flowcam1

hash=d11ab1d441ab12a1f901ede53fdc40bfe23c62c4b384a872a277f62987806061
echo; echo '*** EXPORTING ***'
mdz/mdz export $hash
tree $hash
rm -rf $hash
