
generate
========


**DEPRECATED! Generate universal APK files from Android App Bundles**
### Usage
```bash
universal-apk generate [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--pattern PATTERN]
    [--ks KEYSTORE_PATH]
    [--ks-pass KEYSTORE_PASSWORD]
    [--ks-key-alias KEY_ALIAS]
    [--key-pass KEY_PASSWORD]
```
### Optional arguments for command `universal-apk`

##### `--pattern=PATTERN`


glob pattern to parse files, relative to current folder. Default:&nbsp;`**/*.aab`
##### `--ks=KEYSTORE_PATH`


path to the keystore to sign the apk files with
##### `--ks-pass=KEYSTORE_PASSWORD`


keystore password
##### `--ks-key-alias=KEY_ALIAS`


keystore key alias
##### `--key-pass=KEY_PASSWORD`


keystore key password
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