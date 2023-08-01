
clean
=====


**Clean Xcode project**
### Usage
```bash
xcode-project clean [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--project XCODE_PROJECT_PATH]
    [--workspace XCODE_WORKSPACE_PATH]
    [--target TARGET_NAME]
    [--config CONFIGURATION_NAME]
    [--scheme SCHEME_NAME]
    [--disable-xcpretty]
    [--xcpretty-options OPTIONS]
```
### Optional arguments for action `clean`

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
