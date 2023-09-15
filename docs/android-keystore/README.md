
android-keystore
================


**Manage your Android app code signing keystores**
### Usage
```bash
android-keystore [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
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
|[`create`](create.md)|Create an Android keystore|
|[`create-debug-keystore`](create-debug-keystore.md)|Create Android debug keystore at ~/.android/debug.keystore|
|[`certificate`](certificate.md)|Extract certificate for specified alias from the keystore|
|[`certificates`](certificates.md)|List certificates that are included in keystore|
|[`verify`](verify.md)|Check that the keystore password, key password and key alias are correct for specified keystore|
