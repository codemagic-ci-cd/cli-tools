
Keychain
========


``keychain [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH] ACTION``
#### Utility to manage macOS keychains and certificates

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
### Optional arguments for keychain


**-p, --path=PATH**

Keychain path. If not provided, the system default keychain will be used instead
### Actions

|Action|Description|
| :--- | :--- |
|[add-certificates](keychain_add-certificates.md)|Add p12 certificate to specified keychain.|
|[create](keychain_create.md)|Create a macOS keychain, add it to the search list.|
|[delete](keychain_delete.md)|Delete keychains and remove them from the search list.|
|[get-default](keychain_get-default.md)|Show the system default keychain.|
|[initialize](keychain_initialize.md)|Set up the keychain to be used for code signing. Create the keychain        at specified path with specified password with given timeout.        Make it default and unlock it for upcoming use.|
|[list-certificates](keychain_list-certificates.md)|List available code signing certificates in specified keychain.|
|[lock](keychain_lock.md)|Lock the specified keychain.|
|[make-default](keychain_make-default.md)|Set the keychain as the system default keychain.|
|[set-timeout](keychain_set-timeout.md)|Set timeout settings for the keychain.        If seconds are not provided, then no-timeout will be set.|
|[show-info](keychain_show-info.md)|Show all settings for the keychain.|
|[unlock](keychain_unlock.md)|Unlock the specified keychain.|
