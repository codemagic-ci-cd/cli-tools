
generate
========
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``universal-apk generate [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}]  ``
#### Generate universal APK files from Android App Bundles

### Optional arguments

|Flags|Description|
| :--- | :--- |
|-h, --help|show this help message and exit|

### Options

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### Optional arguments for UniversalApkGenerator

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">--pattern</span>|PATTERN|glob pattern to parse files, relative to current folder|Path|**/*.aab|
|<span style="white-space: nowrap">--bundletool</span>|BUNDLETOOL_PATH|glob pattern to parse files, relative to current folder|Path|/usr/local/bin/bundletool.jar|
|<span style="white-space: nowrap">--ks</span>|KEYSTORE_PATH|path to the keystore to sign the apk files with|Path||
|<span style="white-space: nowrap">--ks-pass</span>|KEYSTORE_PASSWORD|keystore password|str||
|<span style="white-space: nowrap">--ks-key-alias</span>|KEY_ALIAS|keystore key alias|str||
|<span style="white-space: nowrap">--key-pass</span>|KEY_PASSWORD|keystore key password|str||
