
XcodeProject
============

#### Utility to prepare iOS application code signing properties for build


``xcode-project [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION]  ACTION``
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
### Actions

|Action|Description|
| :--- | :--- |
|[build-ipa](xcode-project_build-ipa.md)|Build ipa by archiving the Xcode project and then exporting it|
|[detect-bundle-id](xcode-project_detect-bundle-id.md)|Try to deduce the Bundle ID from specified Xcode project|
|[use-profiles](xcode-project_use-profiles.md)|Set up code signing settings on specified Xcode projects        to use given provisioning profiles|
