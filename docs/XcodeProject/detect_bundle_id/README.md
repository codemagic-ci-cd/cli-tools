
detect_bundle_id
================

#### Try to deduce the Bundle ID from specified Xcode project

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

### Optional arguments for command detect_bundle_id

|Flags|Argument|Description|Type|Default|Multiple arguments|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--project|XCODE_PROJECT_PATTERN|Path to Xcode project (*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory.|Path|**/*.xcodeproj|Yes|
|--target|TARGET_NAME|Name of the Xcode Target|str|||
|--config|CONFIGURATION_NAME|Name of the Xcode build configuration|str|||
