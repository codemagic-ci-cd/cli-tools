
Keychain
========
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``keychain [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] {add_certificates, create, delete, get_default, initialize, list_code_signing_certificates, lock, make_default, set_timeout, show_info, unlock}``
#### Utility to manage macOS keychains and certificates

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

### Keychain actions

|Action|Description|
| :--- | :--- |
|[add_certificates](add_certificates/README.md)|Add p12 certificate to specified keychain.|
|[create](create/README.md)|Create a macOS keychain, add it to the search list.|
|[delete](delete/README.md)|Delete keychains and remove them from the search list.|
|[get_default](get_default/README.md)|Show the system default keychain.|
|[initialize](initialize/README.md)|Set up the keychain to be used for code signing. Create the keychain        at specified path with specified password with given timeout.        Make it default and unlock it for upcoming use.|
|[list_code_signing_certificates](list_code_signing_certificates/README.md)|List available code signing certificates in specified keychain.|
|[lock](lock/README.md)|Lock the specified keychain.|
|[make_default](make_default/README.md)|Set the keychain as the system default keychain.|
|[set_timeout](set_timeout/README.md)|Set timeout settings for the keychain.        If seconds are not provided, then no-timeout will be set.|
|[show_info](show_info/README.md)|Show all settings for the keychain.|
|[unlock](unlock/README.md)|Unlock the specified keychain.|

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">-p, --path</span>|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
