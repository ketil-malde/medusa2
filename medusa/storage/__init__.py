from medusa.storage.files import FileStorage
from medusa.storage.sftp import SftpStorage

def mkstorage(config, create):
    '''Selects storage based on specifier'''
    # repo starts with "HTTP" or "HTTPS"
    # repo starts with "IPFS"
    # repo contains ':'
    if ':' in config['repository']:
        return SftpStorage(config, create)
    else:
        return FileStorage(config, create)

__all__ = [mkstorage, FileStorage, SftpStorage]
