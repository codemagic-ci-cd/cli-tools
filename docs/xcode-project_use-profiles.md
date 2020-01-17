
use_profiles
============


``xcode-project use-profiles [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION]  [--project XCODE_PROJECT_PATTERN] [--profile PROFILE_PATHS] [--export-options-plist EXPORT_OPTIONS_PATH] [--custom-export-options CUSTOM_EXPORT_OPTIONS] ``
#### Set up code signing settings on specified Xcode projects        to use given provisioning profiles

### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream=stderr | stdout**

Log output stream. Default: stderr
### Optional arguments for command use_profiles


**--project=XCODE_PROJECT_PATTERN**

Path to Xcode project (*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory. Multiple arguments. Default:&nbsp;`**/*.xcodeproj`

**--profile=PROFILE_PATHS**

Path to provisioning profile. Can be either a path literal, or a glob pattern to match provisioning profiles. Multiple arguments. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles/*.mobileprovision`

**--export-options-plist=EXPORT_OPTIONS_PATH**

Path to the generated export options plist. Default:&nbsp;`$HOME/export_options.plist`

**--custom-export-options=CUSTOM_EXPORT_OPTIONS**

Custom options for generated export options as JSON string. For example '{"uploadBitcode": false, "uploadSymbols": false}'.