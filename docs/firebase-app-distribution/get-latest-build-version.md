
get-latest-build-version
========================


**Get latest build version from Firebase**
### Usage
```bash
firebase-app-distribution get-latest-build-version [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    --project-number PROJECT_NUMBER
    [--credentials FIREBASE_SERVICE_ACCOUNT_CREDENTIALS]
    --app-id APP_ID
```
### Required arguments for action `get-latest-build-version`

##### `--app-id, -a=APP_ID`


Application ID in Firebase. For example `1:228333310124:ios:5e439e0d0231a788ac8f09`
### Required arguments for command `firebase-app-distribution`

##### `--project-number, -p=PROJECT_NUMBER`


Project Number in Firebase. For example `228333310124`
### Optional arguments for command `firebase-app-distribution`

##### `--credentials, -c=FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`


Firebase service account credentials with JSON key type to access Firebase. If not given, the value will be checked from the environment variable `FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
