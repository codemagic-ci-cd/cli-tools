Various utilities to simplify your builds at [codemagic.io](https://codemagic.io)

# Installing

```
pip3 install codemagic-cli-tools
```

# Usage

Package installs the following executables to your path:

* `app-store-connect`
* `git-changelog`
* `keychain`
* `universal-apk`
* `xcode-project`

See their documentation by running `<command> --help` or `<command> <subcommand> --help`.

For example:

```
universal-apk generate --help
```

All tools have mirroring Python api too:

```python
>>> from codemagic_cli_tools.tools import AppStoreConnect
>>> from codemagic_cli_tools.tools import GitChangelog
>>> from codemagic_cli_tools.tools import Keychain
>>> from codemagic_cli_tools.tools import UniversalApkGenerator
>>> from codemagic_cli_tools.tools import XcodeProject
>>> Keychain().get_default()
PosixPath('/Users/priit/Library/Keychains/login.keychain-db')
...
```
