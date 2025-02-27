
dump
====


**Get files list or extract values from the bundle in a human-readable form**
### Usage
```bash
android-app-bundle dump [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--module DUMP_MODULE]
    [--resource DUMP_RESOURCE]
    [--values]
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

##### `--module=DUMP_MODULE`


Name of the module to apply the dump for. Only applies when dumping the manifest. Defaults to 'base'.
##### `--resource=DUMP_RESOURCE`


Name or ID of the resource to lookup. Only applies when dumping resources. If a resource ID is provided, it can be specified either as a decimal or hexadecimal integer. If a resource name is provided, it must follow the format '<type>/<name>', e.g. 'drawable/icon'
##### `--values`


When set, also prints the values of the resources. Defaults to false. Only applies when dumping the resources.
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
