
add-certificates
================


**Add p12 certificate to specified keychain.**
### Usage
```bash
keychain add-certificates [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-p PATH]
    [-c CERTIFICATE_PATHS]
    [--certificate-password CERTIFICATE_PASSWORD]
    [-a ALLOWED_APPLICATIONS]
    [-A]
    [-D]
```
### Optional arguments for action `add-certificates`

##### `-c, --certificate=CERTIFICATE_PATHS`


Path to pkcs12 certificate. Can be either a path literal, or a glob pattern to match certificates. Multiple arguments. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates/*.p12`
##### `--certificate-password=CERTIFICATE_PASSWORD`


Encrypted p12 certificate password. Alternatively to entering CERTIFICATE_PASSWORD in plaintext, it may also be specified using a "@env:" prefix followed by a environment variable name, or "@file:" prefix followed by a path to the file containing the value. Example: "@env:<variable>" uses the value in the environment variable named "<variable>", and "@file:<file_path>" uses the value from file at "<file_path>". [Default: '']
##### `-a, --allow-app=ALLOWED_APPLICATIONS`


Specify an application which may access the imported key without warning. Multiple arguments. Default:&nbsp;`('/usr/bin/codesign', '/usr/bin/productsign')`
##### `-A, --allow-all-applications`


Allow any application to access the imported key without warning
##### `-D, --disallow-all-applications`


Do not allow any applications to access the imported key without warning
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