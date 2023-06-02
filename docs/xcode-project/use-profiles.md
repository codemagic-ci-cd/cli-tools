
use-profiles
============


**Set up code signing settings on specified Xcode projects         to use given provisioning profiles**
### Usage
```bash
xcode-project use-profiles [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--project XCODE_PROJECT_PATTERN]
    [--profile PROFILE_PATHS]
    [--export-options-plist EXPORT_OPTIONS_PATH]
    [--custom-export-options CUSTOM_EXPORT_OPTIONS]
    [--warn-only]
    [--code-signing-setup-verbose-logging]
    [--archive-method USE_PROFILE_ARCHIVE_METHOD]
```
### Optional arguments for action `use-profiles`

##### `--project=XCODE_PROJECT_PATTERN`


Path to Xcode project (\*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory. Multiple arguments. Default:&nbsp;`**/*.xcodeproj`
##### `--profile=PROFILE_PATHS`


Path to provisioning profile. Can be either a path literal, or a glob pattern to match provisioning profiles. Multiple arguments. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles/*.mobileprovision, $HOME/Library/MobileDevice/Provisioning Profiles/*.provisionprofile`
##### `--export-options-plist=EXPORT_OPTIONS_PATH`


Path to the generated export options plist. Default:&nbsp;`$HOME/export_options.plist`
##### `--custom-export-options=CUSTOM_EXPORT_OPTIONS`


Custom options for generated export options as JSON string. For example, `{"uploadBitcode": false, "uploadSymbols": false}`. If not given, the value will be checked from the environment variable `XCODE_PROJECT_CUSTOM_EXPORT_OPTIONS`. Alternatively to entering `CUSTOM_EXPORT_OPTIONS` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--warn-only`


Show warning when profiles cannot be applied to any of the Xcode projects instead of fully failing the action
##### `--code-signing-setup-verbose-logging`


Show verbose log output when configuring code signing settings for Xcode project. If not given, the value will be checked from the environment variable `XCODE_PROJECT_CODE_SIGNING_SETUP_VERBOSE_LOGGING`.
##### `--archive-method=ad-hoc | app-store | development | enterprise`


Use only the profiles that are eligible for given archive method for code signing setup. If not specified, all found profiles will be used.
### Common options

##### `-h, --help`


show this help message and exit
##### `--log-stream=stderr | stdout`


Log output stream. Default `stderr`
##### `--no-color`


Do not use ANSI colors to format terminal output
##### `--version`


Show tool version and exit
##### `-s, --silent`


Disable log output for commands
##### `-v, --verbose`


Enable verbose logging for commands
