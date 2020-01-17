
build_ipa
=========


``xcode-project build-ipa [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION]  [--project XCODE_PROJECT_PATH] [--workspace XCODE_WORKSPACE_PATH] [--target TARGET_NAME] [--config CONFIGURATION_NAME] [--scheme SCHEME_NAME] [--ipa-directory IPA_DIRECTORY] [--export-options-plist EXPORT_OPTIONS_PATH] [--disable-xcpretty] [--xcpretty-options OPTIONS] ``
#### Build ipa by archiving the Xcode project and then exporting it

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
### Optional arguments for command build_ipa


**--project=XCODE_PROJECT_PATH**

Path to Xcode project (*.xcodeproj)

**--workspace=XCODE_WORKSPACE_PATH**

Path to Xcode workspace (*.xcworkspace)

**--target=TARGET_NAME**

Name of the Xcode Target

**--config=CONFIGURATION_NAME**

Name of the Xcode build configuration

**--scheme=SCHEME_NAME**

Name of the Xcode Scheme

**--ipa-directory=IPA_DIRECTORY**

Directory where the built ipa is stored. Default:&nbsp;`build/ios/ipa`

**--export-options-plist=EXPORT_OPTIONS_PATH**

Path to the generated export options plist. Default:&nbsp;`$HOME/export_options.plist`

**--disable-xcpretty**

Do not use XCPretty formatter to process log output

**--xcpretty-options=OPTIONS**

Command line options for xcpretty formatter (for example "--no-color" or "--simple  --no-utf"). Default:&nbsp;`--color`