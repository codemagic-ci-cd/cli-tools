
android-app-bundle
==================


**Manage Android App Bundles using [Bundletool](https://developer.android.com/studio/command-line/bundletool)**
### Usage
```bash
android-app-bundle [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--bundletool BUNDLETOOL_JAR]
    ACTION
```
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
### Actions

|Action|Description|
| :--- | :--- |
|[`build-apks`](build-apks.md)|Generates an APK Set archive containing either all possible split APKs and standalone APKs or APKs optimized for the connected device (see connected- device flag). Returns list of generated APK set archives|
|[`build-universal-apk`](build-universal-apk.md)|Shortcut for `build-apks` to build universal APKs from bundles|
|[`dump`](dump.md)|Get files list or extract values from the bundle in a human-readable form|
|[`is-signed`](is-signed.md)|Check if given Android app bundle is signed|
|[`sign`](sign.md)|Sign Android app bundle with specified key and keystore|
|[`validate`](validate.md)|Verify that given Android App Bundle is valid and print out information about it|

### Action groups

|Action group|Description|
| :--- | :--- |
|[`bundletool`](bundletool.md)|Show information about Bundletool|
