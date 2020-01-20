
set_timeout
===========


**Set timeout settings for the keychain.        If seconds are not provided, then no-timeout will be set.**
### Usage


``keychain set-timeout [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH] [-t TIMEOUT] ``
### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream=stderr | stdout**

Log output stream. Default: stderr
### Optional arguments for command set_timeout


**-t, --timeout=TIMEOUT**

Keychain timeout in seconds, defaults to no timeout
### Optional arguments for keychain


**-p, --path=PATH**

Keychain path. If not provided, the system default keychain will be used instead