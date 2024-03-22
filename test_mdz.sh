export PYTHONPATH=.

echo '*** VALIDATING ***'
mdz/mdz validate examples/flowcam1

echo; echo '*** IMPORTING ***'
export MDZREPO=/tmp/M
mdz/mdz import examples/flowcam1

hash=2b4c723f9da61467dfe49d0fe1d953a32004fa5be5c8a38a02a7c78864595b20
echo; echo '*** EXPORTING ***'
mdz/mdz export $hash
tree $hash
rm -rf $hash

echo; echo '*** LISTING ***'
mdz/mdz list
