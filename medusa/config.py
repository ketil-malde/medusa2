import os

def get_config():
    config = {}

    # by reversed priority - last overrides (todo: use registry on Windows?)
    for cfile in [os.path.expanduser('~/.mdzrc'), os.path.expanduser('~/.config/mdz')]:
        if os.path.exists(cfile):
            with open(cfile) as f:
                for line in f:
                    name, var = line.partition("=")[::2]
                    config[name.strip()] = var.strip()

    # Env variables can overrule
    if 'MDZREPO' in os.environ: config['repository'] = os.environ['MDZREPO']
    if 'MDZUSERID' in os.environ: config['userid'] = os.environ['MDZUSERID']
    if 'MDZUSERNAME' in os.environ: config['username'] = os.environ['MDZUSERNAME']
    if 'MDZKEY' in os.environ: config['rsakey'] = os.environ['MDZKEY']

    return config
