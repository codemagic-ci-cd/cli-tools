
verify
======


**Check that the keystore password, key password and key alias are correct         for specified keystore**
### Usage
```bash
android-keystore verify [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    -k KEYSTORE_PATH
    -p KEYSTORE_PASSWORD
    -a KEY_ALIAS
```
### Required arguments for action `verify`

##### `-k, --ks, --keystore=KEYSTORE_PATH`


Path where your keystore should be created or read from
##### `-p, --ks-pass, --keystore-pass=KEYSTORE_PASSWORD`


Secure password for your keystore. If not given, the value will be checked from the environment variable `ANDROID_KEYSTORE_PASSWORD`. Alternatively to entering `KEYSTORE_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `-a, --ks-key-alias, --alias=KEY_ALIAS`


An identifying name for your keystore key
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
