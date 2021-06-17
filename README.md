# Codemagic CLI Tools

Command line utilities for managing mobile app builds, code signing, and deployment. These power mobile app builds at [codemagic.io](https://codemagic.io).

# Installing

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```
pip3 install codemagic-cli-tools
```

# CLI Usage

Package installs the following executables to your path:

* [`android-app-bundle`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/android-app-bundle/README.md)
* [`app-store-connect`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/app-store-connect/README.md)
* [`git-changelog`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/git-changelog/README.md)
* [`keychain`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/keychain/README.md)
* [`universal-apk`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/universal-apk/README.md)
* [`xcode-project`](https://github.com/codemagic-ci-cd/cli-tools/blob/master/docs/xcode-project/README.md)

Online documentation for all installed executables can be found under
[`docs`](https://github.com/codemagic-ci-cd/cli-tools/tree/master/docs#cli-tools).

Alternatively, you could see the documentation by using `--help` option from command line:

```bash
<command> --help
```
to see general description and subcommands for the tool, or

```bash
<command> <subcommand> --help
```
to get detailed information of the subcommand.
 
For example:

```
$ keychain create --help
usage: keychain create [-h] [-s] [-v] [--no-color] [--log-stream {stderr,stdout}] [-pw PASSWORD] [-p PATH]

Create a macOS keychain, add it to the search list.

optional arguments:
  -h, --help            show this help message and exit

Options:
  -s, --silent          Disable log output for commands
  -v, --verbose         Enable verbose logging for commands
  --no-color            Do not use ANSI colors to format terminal output
  --log-stream {stderr,stdout}
                        Log output stream. [Default: stderr]

Optional arguments for command create:
  -pw PASSWORD, --password PASSWORD
                        Keychain password. Alternatively to entering PASSWORD in plaintext, it may also be specified using a "@env:" prefix followed by a environment variable name, or "@file:" prefix followed by a path to the file containing the value.
                        Example: "@env:<variable>" uses the value in the environment variable named "<variable>", and "@file:<file_path>" uses the value from file at "<file_path>". [Default: '']

Optional arguments for keychain:
  -p PATH, --path PATH  Keychain path. If not provided, the system default keychain will be used instead
```

# Python API

In addition to the command line interface, the package provides a mirroring Python API too:

```python
>>> from pathlib import Path
>>> from codemagic.tools import AppStoreConnect
>>> from codemagic.tools import GitChangelog
>>> from codemagic.tools import Keychain
>>> from codemagic.tools import UniversalApkGenerator
>>> from codemagic.tools import XcodeProject
>>> Keychain().get_default()
PosixPath('/Users/priit/Library/Keychains/login.keychain-db')
>>> keychain = Keychain(Path('/tmp/new.keychain')) 
>>> keychain.create()
PosixPath('/tmp/new.keychain')
>>> keychain.make_default()
>>> Keychain().get_default()                                                                                                                                                                                                                                        
PosixPath('/private/tmp/new.keychain')
...
```
