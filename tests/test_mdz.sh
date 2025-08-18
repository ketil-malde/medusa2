#!/bin/bash

set -e

export MDZUSERNAME="Test User"
export MDZUSERID=test@example.org
export MDZKEY=~/.ssh/id_rsa
export MDZREPO=/tmp/mdztest2

export PYTHONPATH=.

echo '*** VALIDATING ***'
mdz/mdz validate examples/flowcam1

echo; echo '*** INITIALIZING ***'
mdz/mdz init || echo 'Failed, but probably just because the repo already exists?'

echo; echo '*** IMPORTING ***'
mdz/mdz import examples/flowcam1

hash=2b4c723f9da61467dfe49d0fe1d953a32004fa5be5c8a38a02a7c78864595b20
echo; echo '*** EXPORTING ***'
mdz/mdz export $hash
tree $hash
rm -rf $hash

echo; echo '*** LISTING ***'
mdz/mdz search
echo
mdz/mdz log

echo; echo '*** HTTP test ***'
flask --app mdz/mdzd run &
sleep 5
MDZREPO=http://localhost:5000/ mdz/mdz log
MDZREPO=http://localhost:5000/ mdz/mdz export $hash
tree $hash
rm -rf $hash

echo '*** HTTP prefix test ***'
MDZREPO=http://localhost:5000/ mdz/mdz export ${hash:0:8}
tree ${hash:0:8}
rm -rf ${hash:0:8}

kill %%

