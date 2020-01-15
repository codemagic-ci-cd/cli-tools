
add_certificates
================

#### Add p12 certificate to specified keychain.

### Optional arguments

|Flags|Description|
| :--- | :--- |
|-h, --help|show this help message and exit|

### Options

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### Optional arguments for command add_certificates

|Flags|Argument|Description|Type|Default|Multiple arguments|
| :--- | :--- | :--- | :--- | :--- | :--- |
|-c, --certificate|CERTIFICATE_PATHS|Path to pkcs12 certificate. Can be either a path literal, or a glob pattern to match certificates.|Path|$HOME/Library/MobileDevice/Certificates/*.p12|Yes|
|--certificate-password|CERTIFICATE_PASSWORD|Encrypted p12 certificate password|Password|||

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-p, --path|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
