
XcodeProject
============


``xcode-project [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION]  {build_ipa, detect_bundle_id, use_profiles}``
#### Utility to prepare iOS application code signing properties for build

### Optional arguments

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-h, --help|show this help message and exit||
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### XcodeProject actions

|Action|Description|
| :--- | :--- |
|[build_ipa](XcodeProject_build_ipa.md)|Build ipa by archiving the Xcode project and then exporting it|
|[detect_bundle_id](XcodeProject_detect_bundle_id.md)|Try to deduce the Bundle ID from specified Xcode project|
|[use_profiles](XcodeProject_use_profiles.md)|Set up code signing settings on specified Xcode projects        to use given provisioning profiles|
