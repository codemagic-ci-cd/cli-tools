
unlock
======
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``keychain unlock [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [-pw PASSWORD] ``
#### Unlock the specified keychain.

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

### Optional arguments for command unlock

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-pw, --password|PASSWORD|Keychain password|Password|

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">-p, --path</span>|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
