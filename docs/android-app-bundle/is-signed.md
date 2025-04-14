
is-signed
=========


**Check if given Android app bundle is signed**
### Usage
```bash
android-app-bundle is-signed [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--bundletool BUNDLETOOL_JAR]
    --bundle BUNDLE_PATH
```
### Required arguments for action `is-signed`

##### `--bundle=BUNDLE_PATH`


Path to Android app bundle file
### Optional arguments for command `android-app-bundle`

##### `--bundletool=BUNDLETOOL_JAR`


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
