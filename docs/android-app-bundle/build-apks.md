
build-apks
==========


**Generates an APK Set archive containing either all possible split APKs and         standalone APKs or APKs optimized for the connected device (see connected-         device flag). Returns list of generated APK set archives**
### Usage
```bash
android-app-bundle build-apks [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--bundle BUNDLE_PATTERN]
    [--ks KEYSTORE_PATH]
    [--ks-pass KEYSTORE_PASSWORD]
    [--ks-key-alias KEY_ALIAS]
    [--key-pass KEY_PASSWORD]
    [--mode BUILD_APKS_MODE]
```
### Optional arguments for action `build-apks`

##### `--bundle=BUNDLE_PATTERN`


Glob pattern to parse files, relative to current folder. Default:&nbsp;`**/*.aab`
##### `--ks=KEYSTORE_PATH`


Path to the keystore to sign the apk files with
##### `--ks-pass=KEYSTORE_PASSWORD`


Keystore password. If not given, the value will be checked from the environment variable `KEYSTORE_PASSWORD`. Alternatively to entering `KEYSTORE_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`. [Default: None]
##### `--ks-key-alias=KEY_ALIAS`


Keystore key alias
##### `--key-pass=KEY_PASSWORD`


Keystore key password. If not given, the value will be checked from the environment variable `KEYSTORE_KEY_PASSWORD`. Alternatively to entering `KEY_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`. [Default: None]
##### `--mode=universal`


Set the mode to universal if you want bundletool to build only a single APK that includes all of your app's code and resources such that the APK is compatible with all device configurations your app supports.
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