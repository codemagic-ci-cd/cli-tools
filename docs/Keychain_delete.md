
delete
======


``keychain delete [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH]  ``
#### Delete keychains and remove them from the search list.

### Optional arguments

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-h, --help|show this help message and exit||
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-p, --path|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
