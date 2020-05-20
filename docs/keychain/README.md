
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
|[<nobr><code>add-certificates</code></nobr>](add-certificates.md)|Add p12 certificate to specified keychain.|
|[<nobr><code>create</code></nobr>](create.md)|Create a macOS keychain, add it to the search list.|
|[<nobr><code>delete</code></nobr>](delete.md)|Delete keychains and remove them from the search list.|
|[<nobr><code>get-default</code></nobr>](get-default.md)|Show the system default keychain.|
|[<nobr><code>initialize</code></nobr>](initialize.md)|Set up the keychain to be used for code signing. Create the keychain         at specified path with specified password with given timeout.         Make it default and unlock it for upcoming use.|
|[<nobr><code>list-certificates</code></nobr>](list-certificates.md)|List available code signing certificates in specified keychain.|
|[<nobr><code>lock</code></nobr>](lock.md)|Lock the specified keychain.|
|[<nobr><code>make-default</code></nobr>](make-default.md)|Set the keychain as the system default keychain.|
|[<nobr><code>set-timeout</code></nobr>](set-timeout.md)|Set timeout settings for the keychain.         If seconds are not provided, then no-timeout will be set.|
|[<nobr><code>show-info</code></nobr>](show-info.md)|Show all settings for the keychain.|
|[<nobr><code>unlock</code></nobr>](unlock.md)|Unlock the specified keychain.|
