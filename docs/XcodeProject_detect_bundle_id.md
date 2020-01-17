
detect_bundle_id
================


``xcode-project detect-bundle-id [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION]  [--project XCODE_PROJECT_PATTERN] [--target TARGET_NAME] [--config CONFIGURATION_NAME] ``
#### Try to deduce the Bundle ID from specified Xcode project

### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream={stderr, stdout}**

Log output stream. [Default: stderr]
### Optional arguments for command detect_bundle_id


**--project=XCODE_PROJECT_PATTERN**

Path to Xcode project (*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory. Type `Path`. Multiple arguments. Default: `**/*.xcodeproj`

**--target=TARGET_NAME**

Name of the Xcode Target. Type `str`

**--config=CONFIGURATION_NAME**

Name of the Xcode build configuration. Type `str`