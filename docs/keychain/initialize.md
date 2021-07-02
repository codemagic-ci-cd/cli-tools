
initialize
==========


**Set up the keychain to be used for code signing. Create the keychain         at specified path with specified password with given timeout.         Make it default and unlock it for upcoming use**
### Usage
```bash
keychain initialize [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-p PATH]
    [-pw PASSWORD]
    [-t TIMEOUT]
```
### Optional arguments for action `initialize`

##### `-pw, --password=PASSWORD`


Keychain password. Alternatively to entering `PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`. [Default: '']
##### `-t, --timeout=TIMEOUT`


Keychain timeout in seconds, defaults to no timeout
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