
dump
====


**Get files list or extract values from the bundle in a human-readable form**
### Usage
```bash
android-app-bundle dump [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--xpath DUMP_XPATH]
    DUMP_TARGET
    --bundle BUNDLE_PATH
```
### Required arguments for action `dump`

##### `DUMP_TARGET`


Target of the dump
##### `--bundle=BUNDLE_PATH`


Path to Android app bundle file
### Optional arguments for action `dump`

##### `--xpath=DUMP_XPATH`


XML path to specific attribute in the target. For example "/manifest/@android:versionCode" to obtain the version code from manifest. If not given, the full target will be dumped.
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