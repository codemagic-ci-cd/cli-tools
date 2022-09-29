
build-ipa
=========


**Build ipa by archiving the Xcode project and then exporting it**
### Usage
```bash
xcode-project build-ipa [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--project XCODE_PROJECT_PATH]
    [--workspace XCODE_WORKSPACE_PATH]
    [--target TARGET_NAME]
    [--config CONFIGURATION_NAME]
    [--scheme SCHEME_NAME]
    [--clean]
    [--no-show-build-settings]
    [--archive-directory ARCHIVE_DIRECTORY]
    [--archive-flags ARCHIVE_FLAGS]
    [--archive-xcargs ARCHIVE_XCARGS]
    [--ipa-directory IPA_DIRECTORY]
    [--export-options-plist EXPORT_OPTIONS_PATH]
    [--export-flags EXPORT_FLAGS]
    [--export-xcargs EXPORT_XCARGS]
    [--remove-xcarchive]
    [--disable-xcpretty]
    [--xcpretty-options OPTIONS]
```
### Optional arguments for action `build-ipa`

##### `--project=XCODE_PROJECT_PATH`


Path to Xcode project (\*.xcodeproj)
##### `--workspace=XCODE_WORKSPACE_PATH`


Path to Xcode workspace (\*.xcworkspace)
##### `--target=TARGET_NAME`


Name of the Xcode Target
##### `--config=CONFIGURATION_NAME`


Name of the Xcode build configuration
##### `--scheme=SCHEME_NAME`


Name of the Xcode Scheme
##### `--clean`


Whether to clean the project before building it
##### `--no-show-build-settings`


Do not show build settings for the project before building it. If not given, the value will be checked from the environment variable `XCODE_PROJECT_NO_SHOW_BUILD_SETTINGS`.
##### `--archive-directory=ARCHIVE_DIRECTORY`


Directory where the created archive is stored. Default:&nbsp;`build/ios/xcarchive`
##### `--archive-flags=ARCHIVE_FLAGS`


Pass additional command line options to xcodebuild for the archive phase. For example `-derivedDataPath=$HOME/myDerivedData -quiet`.
##### `--archive-xcargs=ARCHIVE_XCARGS`


Pass additional arguments to xcodebuild for the archive phase. For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`. Default:&nbsp;`COMPILER_INDEX_STORE_ENABLE=NO`
##### `--ipa-directory=IPA_DIRECTORY`


Directory where the built ipa is stored. Default:&nbsp;`build/ios/ipa`
##### `--export-options-plist=EXPORT_OPTIONS_PATH`


Path to the generated export options plist. Default:&nbsp;`$HOME/export_options.plist`
##### `--export-flags=EXPORT_FLAGS`


Pass additional command line options to xcodebuild for the exportArchive phase. For example `-derivedDataPath=$HOME/myDerivedData -quiet`.
##### `--export-xcargs=EXPORT_XCARGS`


Pass additional arguments to xcodebuild for the exportArchive phase. For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`. Default:&nbsp;`COMPILER_INDEX_STORE_ENABLE=NO`
##### `--remove-xcarchive`


Remove generated xcarchive container while building ipa
##### `--disable-xcpretty`


Do not use XCPretty formatter to process log output
##### `--xcpretty-options=OPTIONS`


Command line options for xcpretty formatter. For example "--no-color" or "--simple  --no-utf". Default:&nbsp;`--color`
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