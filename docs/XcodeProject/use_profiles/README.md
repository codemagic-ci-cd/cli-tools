
use_profiles
============

#### Set up code signing settings on specified Xcode projects        to use given provisioning profiles

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

### Optional arguments for command use_profiles

|Flags|Argument|Description|Type|Default|Multiple arguments|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--project|XCODE_PROJECT_PATTERN|Path to Xcode project (*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory.|Path|**/*.xcodeproj|Yes|
|--profile|PROFILE_PATHS|Path to provisioning profile. Can be either a path literal, or a glob pattern to match provisioning profiles.|Path|$HOME/Library/MobileDevice/Provisioning Profiles/*.mobileprovision|Yes|
|--export-options-plist|EXPORT_OPTIONS_PATH|Path to the generated export options plist|Path|$HOME/export_options.plist||
|--custom-export-options|CUSTOM_EXPORT_OPTIONS|Custom options for generated export options as JSON string. For example '{"uploadBitcode": false, "uploadSymbols": false}'.|_json_dict|||
