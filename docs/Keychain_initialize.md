
initialize
==========


``keychain initialize [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH] [-pw PASSWORD] [-t TIMEOUT] ``
#### Set up the keychain to be used for code signing. Create the keychain        at specified path with specified password with given timeout.        Make it default and unlock it for upcoming use.

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
### Optional arguments for command initialize


**-pw, --password=PASSWORD**

Keychain password

**-t, --timeout=TIMEOUT**

Keychain timeout in seconds, defaults to no timeout
### Optional arguments for keychain


**-p, --path=PATH**

Keychain path. If not provided, the system default keychain will be used instead