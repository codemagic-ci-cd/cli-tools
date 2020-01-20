
generate
========


**Generate universal APK files from Android App Bundles**
### Usage


``universal-apk generate [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--pattern PATTERN] [--bundletool BUNDLETOOL_PATH] [--ks KEYSTORE_PATH] [--ks-pass KEYSTORE_PASSWORD] [--ks-key-alias KEY_ALIAS] [--key-pass KEY_PASSWORD]  ``
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
### Optional arguments for universal-apk


**--pattern=PATTERN**

glob pattern to parse files, relative to current folder. Default:&nbsp;`**/*.aab`

**--bundletool=BUNDLETOOL_PATH**

glob pattern to parse files, relative to current folder. Default:&nbsp;`/usr/local/bin/bundletool.jar`

**--ks=KEYSTORE_PATH**

path to the keystore to sign the apk files with

**--ks-pass=KEYSTORE_PASSWORD**

keystore password

**--ks-key-alias=KEY_ALIAS**

keystore key alias

**--key-pass=KEY_PASSWORD**

keystore key password