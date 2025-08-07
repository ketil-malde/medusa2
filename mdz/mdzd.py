#!/usr/bin/env python3
# Server

import flask
from medusa.storage import mkstorage
from medusa.config import get_config
from medusa.util import error
from os import remove

# Set up MDZ repository as normal
config = get_config()
assert 'repository' in config.keys(), error('Repository not specified, set $MDZREPO')
fs = mkstorage(config, create=False)

server = flask.Flask(__name__)

@server.route('/', methods=['GET'])
def get_root():
    print('Requesting repository HEAD')
    return fs.gethead()

@server.route('/', methods=['POST'])
def set_root():
    print('Setting repository HEAD')
    fs.sethead(flask.request.data.decode())
    return 'Set HEAD', 200

@server.route('/put/', methods=['POST'])
def put_object():
    myhash = fs.puts(flask.request.data)
    print(f'Posted id: {myhash}')
    return myhash, 200

@server.route('/get/<id>', methods=['HEAD'])
def check_object(id):
    print(f'Testing for {id}')
    idx = fs.expand_prefix(id)
    if fs.exists(id):
        return 'Object {id} exists', 200
    elif len(idx) == 1 and fs.exists(idx[0]):
        return 'Object {id} is a valid prefix for {idx[0]}', 200
    elif len(idx) > 1:
        return 'Prefix {id} is ambiguous', 404
    else:
        return 'Object {id} does not exist', 404

@server.route('/get/<id>', methods=['GET'])
def get_object(id):
    # see: https://stackoverflow.com/questions/11017466/flask-to-return-image-stored-in-database
    # flask.send_file(path_or_file, mimetype=None, as_attachment=False, download_name=None, conditional=True, etag=True, last_modified=None, max_age=None)

    print(f'Requesting {id}')
    if fs.exists(id):
        idx = id
    else:
        ids = fs.expand_prefix(id)
        if len(ids) == 1:
            idx = ids[0]
        else:
            return f'Object {id} not found.', 404

    tmpfile = '/tmp/mdztmpfile'
    try:
        remove(tmpfile)
    except Exception:
        pass
    fs.get(idx, fname=tmpfile)
    return flask.send_file(tmpfile, as_attachment=False)
