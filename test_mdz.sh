export PYTHONPATH=.

echo '*** VALIDATING ***'
mdz/mdz validate examples/flowcam1

echo; echo '*** IMPORTING ***'
export MDZREPO=/tmp/M
mdz/mdz import examples/flowcam1

hash=2a6ec2b387fb718d8c9a7ac213bc3550cb2b4862c99604d73fbc6aa7fdffcf9d
echo; echo '*** EXPORTING ***'
mdz/mdz export $hash
tree $hash
rm -rf $hash
