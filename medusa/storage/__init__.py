from medusa.storage.files import FileStorage
from medusa.storage.http import HttpStorage
from medusa.storage.sftp import SftpStorage
from medusa.storage.ipfs import IpfsStorage

def mkstorage(config, create):
    '''Selects storage based on specifier'''
    # repo starts with "IPFS"
    if config['repository'][:5] == 'ipfs:':
        return IpfsStorage(config, create)
    # repo starts with "HTTP" or "HTTPS"
    elif config['repository'][:4] == 'http':
        return HttpStorage(config)
    elif ':' in config['repository']:
        return SftpStorage(config, create)
    else:
        return FileStorage(config, create)

__all__ = [mkstorage, FileStorage, SftpStorage, HttpStorage, IpfsStorage]
