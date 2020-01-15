
build_ipa
=========

#### Build ipa by archiving the Xcode project and then exporting it

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

### Optional arguments for command build_ipa

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--project|XCODE_PROJECT_PATH|Path to Xcode project (*.xcodeproj)|_existing_path||
|--workspace|XCODE_WORKSPACE_PATH|Path to Xcode workspace (*.xcworkspace)|_existing_path||
|--target|TARGET_NAME|Name of the Xcode Target|str||
|--config|CONFIGURATION_NAME|Name of the Xcode build configuration|str||
|--scheme|SCHEME_NAME|Name of the Xcode Scheme|str||
|--ipa-directory|IPA_DIRECTORY|Directory where the built ipa is stored|Path|build/ios/ipa|
|--export-options-plist|EXPORT_OPTIONS_PATH|Path to the generated export options plist|Path|$HOME/export_options.plist|
|--disable-xcpretty|DISABLE|Do not use XCPretty formatter to process log output|bool||
|--xcpretty-options|OPTIONS|Command line options for xcpretty formatter (for example "--no-color" or "--simple  --no-utf")|str|--color|
