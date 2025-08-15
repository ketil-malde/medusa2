import subprocess
import os
import base58
from multiformats import CID
from medusa.util import error
import urllib

def _cid_to_hex(cid_str):
    """Convert a CID (base58 or base32) to a hex-encoded SHA-256 multihash."""
    try:
        if isinstance(cid_str, str):
            cid = CID.decode(cid_str)
        else:
            cid = CID.decode(cid_str.decode('utf-8'))
    except Exception as e:
        print('Decode failed: ', cid_str, e)
    if cid.hashfun.code != 0x12:
        error(f"CID {cid_str} uses non-SHA-256 hash (code: {cid.hashfun.code})")
    return cid.digest.hex()[4:]

def _hex_to_cid(hex_hash):
    """Convert a hex-encoded SHA-256 multihash to a CIDv0."""
    hash_bytes = bytes.fromhex(hex_hash)
    if len(hash_bytes) != 32:
        error(f'Hex hash must be 32 bytes (64 hex chars) for SHA-256, found {len(hash_bytes)}.')
    mh_bytes = b'\x12\x20' + hash_bytes
    cid = base58.b58encode(mh_bytes).decode('utf-8')
    return cid

class IpfsStorage:
    def __init__(self, config, create=False, ipfs_cmd='ipfs'):
        """Initialize with the path to the ipfs CLI command."""
        self.head = os.path.expanduser(config['head']) if 'head' in config else os.path.expanduser('~/.mdzhead')

        parsed_url = urllib.parse.urlparse(config['repository'])
        if parsed_url.scheme != 'ipfs':
            error(f'IPFS node URL must start with ipfs:// (found {parsed_url.scheme})')
        self.host = parsed_url.hostname
        # TODO: socket.getaddrinfo to extract IP from hostname
        self.port = parsed_url.port or 5001
        self.api_multiaddr = f"/ip4/{self.host}/tcp/{self.port}"
        self.ipfs_cmd = ipfs_cmd
        try:
            subprocess.run([self.ipfs_cmd, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            error(f'IPFS CLI not found. Ensure \'{ipfs_cmd}\' is installed and in $PATH.')

        if create:
            with open(self.head, 'w') as h:
                h.write('None')
        else:
            pass

    def exists(self, fhash):
        """Check if fhash exists in storage"""
        pass

    def expand_prefix(self, fhash):
        """Not supported here, I'm afraid"""
        error('Expanding prefixes not supported for IPFS')

    def put(self, file_path):
        """Add a local file to IPFS and return its CID."""
        if not os.path.exists(file_path):
            error(f"File {file_path} does not exist")
        try:
            result = subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'add', '--raw-leaves', '--cid-version=1', '-Q', file_path],
                capture_output=True,
                text=True,
                check=True
            )
            cid = result.stdout.strip()
            print(f"Added {file_path} with CID: {cid}")
            return _cid_to_hex(cid)
        except subprocess.CalledProcessError as e:
            error(f"Failed to add file to IPFS: {e.stderr}")

    def puts(self, mybstring):
        """Put a bytestring object in storage"""
        try:
            result = subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'add', '--raw-leaves', '--cid-version=1', '-Q'],
                capture_output=True,
                input=mybstring,
                text=False,
                check=True
            )
            cid = result.stdout.strip()
            print(f"Added new object with CID: {cid}")
            return _cid_to_hex(cid)
        except subprocess.CalledProcessError as e:
            error(f"Failed to add file to IPFS: {e.stderr}")

    def get(self, myhash, output_path):
        """Download a file from IPFS by CID to a local path."""
        try:
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'get', _hex_to_cid(myhash), '-o', output_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Downloaded {myhash} to {output_path}")
        except subprocess.CalledProcessError as e:
            error(f"Failed to download file from IPFS: {e.stderr}")

    def gets(self, hex_hash):
        """Retrieve the contents of an IPFS file by 64-character hex-encoded SHA-256 digest as a string."""
        try:
            result = subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'cat', _hex_to_cid(hex_hash)],
                capture_output=True,
                text=True,
                check=True
            )
            content = result.stdout
            print(f"Retrieved content for {hex_hash}")
            return content
        except subprocess.CalledProcessError as e:
            error(f"Failed to read file from IPFS: {e.stderr}")

    def gethead(self):
        with open(self.head, 'r') as f:
            return f.readline()

    def sethead(self, myhash):
        with open(self.head, 'w') as f:
            return f.write(f'{myhash}')
