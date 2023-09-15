
set-timeout
===========


**Set timeout settings for the keychain. If seconds are not provided, then no-timeout will be set**
### Usage
```bash
keychain set-timeout [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-p PATH]
    [-t TIMEOUT]
```
### Optional arguments for action `set-timeout`

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
