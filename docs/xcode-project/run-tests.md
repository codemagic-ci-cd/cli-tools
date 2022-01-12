
run-tests
=========


**Run unit or UI tests for given Xcode project or workspace**
### Usage
```bash
xcode-project run-tests [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--project XCODE_PROJECT_PATH]
    [--workspace XCODE_WORKSPACE_PATH]
    [--target TARGET_NAME]
    [--config CONFIGURATION_NAME]
    [--scheme SCHEME_NAME]
    [--clean]
    [--disable-coverage]
    [--graceful-exit]
    [--max-concurrent-devices MAX_CONCURRENT_DEVICES]
    [--max-concurrent-simulators MAX_CONCURRENT_SIMULATORS]
    [-d TEST_DEVICES]
    [--test-only TEST_ONLY]
    [--sdk TEST_SDK]
    [-o OUTPUT_DIRECTORY]
    [-e OUTPUT_EXTENSION]
    [--test-flags TEST_FLAGS]
    [--test-xcargs TEST_XCARGS]
    [--disable-xcpretty]
    [--xcpretty-options OPTIONS]
```
### Optional arguments for action `run-tests`

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
##### `--disable-coverage`


Turn code coverage off when testing
##### `--graceful-exit`


In case of failed tests or unsuccessful test run exit the program with status code 0
##### `--max-concurrent-devices=MAX_CONCURRENT_DEVICES`


The maximum number of device destinations to test on concurrently.
##### `--max-concurrent-simulators=MAX_CONCURRENT_SIMULATORS`


The maximum number of simulator destinations to test on concurrently.
##### `-d, --device=TEST_DEVICES`


Test destination description. Either a UDID value of the device, or device name and runtime combination. If runtime is not specified, the latest available runtime for given device name will be chosen. For example "iOS 14.0 iPhone SE (2nd generation)", "iPad Pro (9.7-inch)", "tvOS 14.1 Apple TV 4K (at 1080p)", "Apple TV 4K". Default test destination will be chosen if no devices are specified and test SDK is not targeting macOS. For macOS tests no destination are specified. (See `xcode-project default-test-destination` for more information about default destination). Multiple arguments
##### `--test-only=TEST_ONLY`


Limit test run to execute only specified tests, and exclude all other tests
##### `--sdk=TEST_SDK`


Name of the SDK that should be used for building the application for testing. Default:&nbsp;`iphonesimulator`
##### `-o, --output-dir=OUTPUT_DIRECTORY`


Directory where the Junit XML results will be saved. Default:&nbsp;`build/ios/test`
##### `-e, --output-extension=OUTPUT_EXTENSION`


Extension for the created Junit XML file. For example `xml` or `junit`. Default:&nbsp;`xml`
##### `--test-flags=TEST_FLAGS`


Pass additional command line options to xcodebuild for the test phase. For example `-derivedDataPath=$HOME/myDerivedData -quiet`.
##### `--test-xcargs=TEST_XCARGS`


Pass additional arguments to xcodebuild for the test phase. For example `COMPILER_INDEX_STORE_ENABLE=NO OTHER_LDFLAGS="-ObjC -lstdc++`.
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