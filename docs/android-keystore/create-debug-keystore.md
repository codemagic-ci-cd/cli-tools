
create-debug-keystore
=====================


**Create Android debug keystore at ~/.android/debug.keystore**
### Usage
```bash
android-keystore create-debug-keystore [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-o]
    [--validity VALIDITY_DAYS]
```
### Optional arguments for action `create-debug-keystore`

##### `-o, --overwrite-existing`


Overwrite keystore at specified path in case it exists
##### `--validity=VALIDITY_DAYS`


How long will the keystore be valid in days. Default:&nbsp;`10000`
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
