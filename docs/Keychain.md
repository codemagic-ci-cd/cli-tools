
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

**--log-stream={stderr, stdout}**

Log output stream. [Default: stderr]
### Optional arguments for Keychain


**-p, --path=PATH**

Keychain path. If not provided, the system default keychain will be used instead. Type `Path`
### Actions

|Action|Description|
| :--- | :--- |
|[add_certificates](Keychain_add_certificates.md)|Add p12 certificate to specified keychain.|
|[create](Keychain_create.md)|Create a macOS keychain, add it to the search list.|
|[delete](Keychain_delete.md)|Delete keychains and remove them from the search list.|
|[get_default](Keychain_get_default.md)|Show the system default keychain.|
|[initialize](Keychain_initialize.md)|Set up the keychain to be used for code signing. Create the keychain        at specified path with specified password with given timeout.        Make it default and unlock it for upcoming use.|
|[list_code_signing_certificates](Keychain_list_code_signing_certificates.md)|List available code signing certificates in specified keychain.|
|[lock](Keychain_lock.md)|Lock the specified keychain.|
|[make_default](Keychain_make_default.md)|Set the keychain as the system default keychain.|
|[set_timeout](Keychain_set_timeout.md)|Set timeout settings for the keychain.        If seconds are not provided, then no-timeout will be set.|
|[show_info](Keychain_show_info.md)|Show all settings for the keychain.|
|[unlock](Keychain_unlock.md)|Unlock the specified keychain.|
