
info
====


**Show full information about Bundletool runtime environment**
### Usage
```bash
android-app-bundle bundletool info [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--bundletool BUNDLETOOL_JAR]
    [--json]
```
### Optional arguments for action `info`

##### `--json`


Whether to show the information in JSON format
### Optional arguments for command `android-app-bundle`

##### `--bundletool, -j=BUNDLETOOL_JAR`


Specify path to bundletool jar that will be used in place of the included version. If not given, the value will be checked from the environment variable `ANDROID_APP_BUNDLE_BUNDLETOOL`.
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
