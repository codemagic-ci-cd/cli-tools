
create
======


``keychain create [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [-p PATH] [-pw PASSWORD] ``
#### Create a macOS keychain, add it to the search list.

### Optional arguments

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-h, --help|show this help message and exit||
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### Optional arguments for command create

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-pw, --password|PASSWORD|Keychain password|Password|

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-p, --path|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
