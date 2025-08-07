# Medusa: a metadata-oriented decentralized universal storage

Medusa is a simple system for managing data sets as collection of
files, described using a simple metadata format.  It uses
cryptographic signatures to identify data objects (Content-Adressable
Storage, similar to Git), and maintains a block-chain ledger of
its operations.

## Usage

The command line tool, `mdz` provides access to most of the
functionality. It requires an address for the repository, a user-id,
and an RSA key.  This can be configured in a config file `.mdzrc` (or `.config/mdz`):

    username   = Ketil Malde
    userid     = ketil@malde.org
    rsakey     = ~/.ssh/id_rsa
    repository = /tmp/medusa

The values can be overriden by the environment variables `MDZREPO`,
`MDZUSERID`, `MDZUSERNAME`, and `MDZKEY`.

If the repository is an SSH path (e.g.,
`ketil@malde.org:/tmp/medusa`), `mdz` will recognize that and use
SFTP, if not, it will work directly on the file system.  An alternative
transport is HTTP, specified as `http://host:port/`.  This expects to talk 
a server, `mdzd`, which uses the same config as `mdz`.

Possible commands are:

- `mdz init` - initialize a repository
- `mdz log` - list repository ledger entries
- `mdz search` - show datasets
- `mdz validate` - validate a local data set
- `mdz import` - copy a local data set into the repository
- `mdz export` - extract a data set from the repository

(To be continued)
