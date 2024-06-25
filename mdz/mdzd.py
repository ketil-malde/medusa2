#!/usr/bin/env python3
# Server

import flask
from medusa.storage import mkstorage
from os import path, remove

# Set up MDZ repository as normal
config = {'username': 'Ketil Malde',
          'userid': 'ketil@malde.org',
          'rsakey': '~/.ssh/id_rsa',
          'repository': '/tmp/mdz'}

fs = mkstorage(config, create=False)

server = flask.Flask(__name__)

@server.route('/', methods=['GET'])
def get_root():
    print('Requesting repository HEAD')
    return fs.gethead()


@server.route('/', methods=['POST'])
def put_object():
    myhash = fs.puts(flask.request.data)  # fuck this shit.
    print(f'Posted id: {myhash}')
    return myhash, 200


@server.route('/<id>', methods=['HEAD'])
def check_object(id):
    print(f'Testing for {id}')
    if fs.exists(id):
        return 'Object {id} exists', 200
    else:
        return 'Object {id} does not exist', 404


@server.route('/<id>', methods=['GET'])
def get_object(id):
    # see: https://stackoverflow.com/questions/11017466/flask-to-return-image-stored-in-database
    # flask.send_file(path_or_file, mimetype=None, as_attachment=False, download_name=None, conditional=True, etag=True, last_modified=None, max_age=None)

    print(f'Requesting {id}')
    if fs.exists(id):
        tmpfile = '/tmp/mdztmpfile'
        try:
            remove(tmpfile)
        except Exception:
            pass
        fs.get(id, fname=tmpfile)
        return flask.send_file(tmpfile, as_attachment=False)
    else:
        return f'Object {id} not found.', 404
