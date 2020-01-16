
lock
====


``keychain lock [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}]  ``
#### Lock the specified keychain.

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

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-p, --path|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
