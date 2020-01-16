
set_timeout
===========
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``keychain set-timeout [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [-t TIMEOUT] ``
#### Set timeout settings for the keychain.        If seconds are not provided, then no-timeout will be set.

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

### Optional arguments for command set_timeout

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|-t, --timeout|TIMEOUT|Keychain timeout in seconds, defaults to no timeout|Seconds|

### Optional arguments for Keychain

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">-p, --path</span>|PATH|Keychain path. If not provided, the system default keychain will be used instead|Path|
