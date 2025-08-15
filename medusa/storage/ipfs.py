import subprocess
import os
import base58
import base64
from multiformats import CID
from medusa.util import error
import urllib

def _cid_to_hex(cid_str):
    """Convert a CID (base58 or base32) to a hex-encoded SHA-256 multihash."""
    if not isinstance(cid_str, str):
        cid_str = cid_str.decode('utf-8')
    cid_str_padded = cid_str[1:] + '=' * ((8 - len(cid_str[1:]) % 8) % 8)
    print('cid_str_padded = ', cid_str_padded)
    cid_bytes = base64.b32decode(cid_str_padded.upper())
    print('cid2hex:', cid_bytes, type(cid_bytes))
    assert cid_bytes[0] == 0x01 and cid_bytes[1] == 0x55, f'CID Prefix {cid_bytes[:2]} indicates not CIDv1 with raw.'
    assert cid_bytes[2] == 0x12 and cid_bytes[3] == 0x20, f'CID not using sha256 (code {cid_bytes[2]} not 0x12).'
    assert len(cid_bytes) == 4 + 32, f'CID length is {len(cid_bytes)}, not 4+32'

    print('hex hash', cid_bytes[4:].hex())
    return cid_bytes[4:].hex()

def _hex_to_cid(hex_hash):
    """Convert a hex-encoded SHA-256 multihash to a CIDv0."""
    hash_bytes = bytes.fromhex(hex_hash)
    if len(hash_bytes) != 32:
        raise f'Hex hash must be 32 bytes (64 hex chars) for SHA-256, found {len(hash_bytes)}.'
    mh_bytes = b'\x01\x55\x12\x20' + hash_bytes
    cid = 'b' + base64.b32encode(mh_bytes).decode('utf-8').lower()
    print(f'hex2cid:, {hex_hash} -> {cid}')
    return cid.rstrip('=')

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
            chunk_size = max(1048576, os.path.getsize(file_path))
            result = subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'add', '--raw-leaves', '--cid-version=1', f'--chunker=size-{chunk_size}', '-Q', file_path],
                capture_output=True,
                text=True,
                check=True
            )
            cid = result.stdout.strip()
            print(f"Added {file_path} with CID: {cid}")
            assert len(_cid_to_hex(cid)) == 64, f'wrong length for {len(_cid_to_hex(cid))}\n {cid} -> {_cid_to_hex(cid)})!'
            return _cid_to_hex(cid)
        except subprocess.CalledProcessError as e:
            error(f"Failed to add file to IPFS: {e.stderr}")

    def puts(self, mybstring):
        """Put a bytestring object in storage"""
        chunk_size = max(1048576, len(mybstring))
        try:
            result = subprocess.run(
                [self.ipfs_cmd, '--api', self.api_multiaddr, 'add', '--raw-leaves', '--cid-version=1', f'--chunker=size-{chunk_size}', '-Q'],
                capture_output=True,
                input=mybstring,
                text=False,
                check=True
            )
            cid = result.stdout.strip()
            print(f"Added new object with CID: {cid}")
            assert len(_cid_to_hex(cid)) == 64, f'wrong length {len(_cid_to_hex(cid))}\n {cid} -> {_cid_to_hex(cid)})!'
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
        print('gets: ', [self.ipfs_cmd, '--api', self.api_multiaddr, 'cat', _hex_to_cid(hex_hash)])
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
            error(f"Failed to read contents from IPFS: {e.stderr}")

    def gethead(self):
        with open(self.head, 'r') as f:
            return f.readline()

    def sethead(self, myhash):
        assert len(myhash) == 64, f'Wrong hash lenght for HEAD: {myhash}'
        with open(self.head, 'w') as f:
            return f.write(f'{myhash}')
