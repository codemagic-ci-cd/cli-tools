
UniversalApkGenerator
=====================


``universal-apk [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--pattern PATTERN] [--bundletool BUNDLETOOL_PATH] [--ks KEYSTORE_PATH] [--ks-pass KEYSTORE_PASSWORD] [--ks-key-alias KEY_ALIAS] [--key-pass KEY_PASSWORD] {generate}``
#### Generate universal APK files from Android App Bundles

### Optional arguments

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-h, --help|show this help message and exit||
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### UniversalApkGenerator actions

|Action|Description|
| :--- | :--- |
|[generate](UniversalApkGenerator_generate.md)|Generate universal APK files from Android App Bundles|

### Optional arguments for UniversalApkGenerator

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--pattern|PATTERN|glob pattern to parse files, relative to current folder|Path|**/*.aab|
|--bundletool|BUNDLETOOL_PATH|glob pattern to parse files, relative to current folder|Path|/usr/local/bin/bundletool.jar|
|--ks|KEYSTORE_PATH|path to the keystore to sign the apk files with|Path||
|--ks-pass|KEYSTORE_PASSWORD|keystore password|str||
|--ks-key-alias|KEY_ALIAS|keystore key alias|str||
|--key-pass|KEY_PASSWORD|keystore key password|str||
