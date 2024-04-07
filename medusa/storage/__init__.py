from medusa.storage.files import FileStorage

def mkstorage(config, create):
    '''Selects storage based on specifier'''
    # repo starts with "HTTP" or "HTTPS"
    # repo starts with "IPFS"
    # otherwise
    return FileStorage(config, create)

__all__ = [mkstorage, FileStorage]
