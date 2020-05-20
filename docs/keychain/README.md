
keychain
========


**Utility to manage macOS keychains and certificates**
### Usage
```bash
keychain [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-p PATH]
    ACTION
```
### Optional arguments for command `keychain`

##### `-p, --path=PATH`


Keychain path. If not provided, the system default keychain will be used instead
### Common options

##### `-h, --help`


show this help message and exit
##### `--log-stream=stderr | stdout`


Log output stream. Default `stderr`
##### `--no-color`


Do not use ANSI colors to format terminal output
##### `--version`


Show tool version and exit
##### `-s, --silent`


Disable log output for commands
##### `-v, --verbose`


Enable verbose logging for commands
### Actions

|Action|Description|
| :--- | :--- |
|[`add‑certificates`](add-certificates.md)|Add p12 certificate to specified keychain.|
|[`create`](create.md)|Create a macOS keychain, add it to the search list.|
|[`delete`](delete.md)|Delete keychains and remove them from the search list.|
|[`get‑default`](get-default.md)|Show the system default keychain.|
|[`initialize`](initialize.md)|Set up the keychain to be used for code signing. Create the keychain         at specified path with specified password with given timeout.         Make it default and unlock it for upcoming use.|
|[`list‑certificates`](list-certificates.md)|List available code signing certificates in specified keychain.|
|[`lock`](lock.md)|Lock the specified keychain.|
|[`make‑default`](make-default.md)|Set the keychain as the system default keychain.|
|[`set‑timeout`](set-timeout.md)|Set timeout settings for the keychain.         If seconds are not provided, then no-timeout will be set.|
|[`show‑info`](show-info.md)|Show all settings for the keychain.|
|[`unlock`](unlock.md)|Unlock the specified keychain.|
