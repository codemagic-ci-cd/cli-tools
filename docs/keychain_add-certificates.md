
add_certificates
================


``keychain add-certificates [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH] [-c CERTIFICATE_PATHS] [--certificate-password CERTIFICATE_PASSWORD] ``
#### Add p12 certificate to specified keychain.

### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream=stderr|stdout**

Log output stream. Default: stderr
### Optional arguments for command add_certificates


**-c, --certificate=CERTIFICATE_PATHS**

Path to pkcs12 certificate. Can be either a path literal, or a glob pattern to match certificates. Multiple arguments. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates/*.p12`

**--certificate-password=CERTIFICATE_PASSWORD**

Encrypted p12 certificate password
### Optional arguments for keychain


**-p, --path=PATH**

Keychain path. If not provided, the system default keychain will be used instead