
XcodeProject
============
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``xcode-project [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] {build_ipa, detect_bundle_id, use_profiles}``
#### Utility to prepare iOS application code signing properties for build

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

### XcodeProject actions

|Action|Description|
| :--- | :--- |
|[build_ipa](build_ipa/README.md)|Build ipa by archiving the Xcode project and then exporting it|
|[detect_bundle_id](detect_bundle_id/README.md)|Try to deduce the Bundle ID from specified Xcode project|
|[use_profiles](use_profiles/README.md)|Set up code signing settings on specified Xcode projects        to use given provisioning profiles|
