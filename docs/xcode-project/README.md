
xcode-project
=============


**Utility to work with Xcode projects. Use it to manage iOS application     code signing properties for builds, create IPAs and run tests**
### Usage
```bash
xcode-project [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    ACTION
```
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
### Actions

|Action|Description|
| :--- | :--- |
|[`build-ipa`](build-ipa.md)|Build ipa by archiving the Xcode project and then exporting it|
|[`clean`](clean.md)|Clean Xcode project|
|[`junit-test-results`](junit-test-results.md)|Convert Xcode Test Result Bundles (*.xcresult) to JUnit XML format|
|[`detect-bundle-id`](detect-bundle-id.md)|Try to deduce the Bundle ID from specified Xcode project|
|[`default-test-destination`](default-test-destination.md)|Show default test destination for the chosen Xcode version|
|[`ipa-info`](ipa-info.md)|Show information about iOS App Store Package file|
|[`pkg-info`](pkg-info.md)|Show information about macOS Application Package file|
|[`test-destinations`](test-destinations.md)|List available destinations for test runs|
|[`run-tests`](run-tests.md)|Run unit or UI tests for given Xcode project or workspace|
|[`test-summary`](test-summary.md)|Show summary of Xcode Test Result|
|[`use-profiles`](use-profiles.md)|Set up code signing settings on specified Xcode projects         to use given provisioning profiles|
