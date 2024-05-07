#!/bin/bash

set -e

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
