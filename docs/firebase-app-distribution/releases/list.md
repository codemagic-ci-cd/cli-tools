
list
====


**List releases for the Firebase application**
### Usage
```bash
firebase-app-distribution releases list [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    --project-id PROJECT_ID
    [--credentials FIREBASE_SERVICE_ACCOUNT_CREDENTIALS]
    [--limit LIMIT]
    [--order-by ORDER_BY]
    [--json]
    --app-id APP_ID
```
### Required arguments for action `list`

##### `--app-id, -a=APP_ID`


Application ID in Firebase. For example 1:228333310124:ios:5e439e0d0231a788ac8f09
### Optional arguments for action `list`

##### `--limit, -l=LIMIT`


The number of resources to list. Default:&nbsp;`25`
##### `--order-by, -o=createTimeDesc | createTime`


Sort resources in the specified order. Default:&nbsp;`createTimeDesc`
##### `--json, -j`


Whether to show the request response in JSON format
### Required arguments for command `firebase-app-distribution`

##### `--project-id, -p=PROJECT_ID`


Project ID in Firebase. For example 228333310124
### Optional arguments for command `firebase-app-distribution`

##### `--credentials, -c=FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`


Firebase service account credentials with `JSON` key type to access Firebase. If not given, the value will be checked from the environment variable `FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
