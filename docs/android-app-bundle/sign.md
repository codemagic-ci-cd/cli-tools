
sign
====


**Sign Android app bundle with specified key and keystore**
### Usage
```bash
android-app-bundle sign [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--bundletool BUNDLETOOL_JAR]
    --bundle BUNDLE_PATH
    --ks KEYSTORE_PATH_REQUIRED
    --ks-pass KEYSTORE_PASSWORD_REQUIRED
    --ks-key-alias KEY_ALIAS_REQUIRED
    --key-pass KEY_PASSWORD_REQUIRED
```
### Required arguments for action `sign`

##### `--bundle=BUNDLE_PATH`


Path to Android app bundle file
##### `--ks=KEYSTORE_PATH_REQUIRED`


Path to the keystore to sign the apk files with
##### `--ks-pass=KEYSTORE_PASSWORD_REQUIRED`


Keystore password. If not given, the value will be checked from the environment variable `KEYSTORE_PASSWORD`. Alternatively to entering `KEYSTORE_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--ks-key-alias=KEY_ALIAS_REQUIRED`


Keystore key alias
##### `--key-pass=KEY_PASSWORD_REQUIRED`


Keystore key password. If not given, the value will be checked from the environment variable `KEYSTORE_KEY_PASSWORD`. Alternatively to entering KEY_PASSWORD in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
