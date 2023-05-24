
releases
========


**Manage your Firebase releases**
### Usage
```bash
firebase releases [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials FIREBASE_SERVICE_ACCOUNT_CREDENTIALS]
    ACTION
```
### Optional arguments for command `firebase`

##### `--credentials=FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`


Firebase service account credentials with `JSON` key type to access Firebase API. If not given, the value will be checked from the environment variable `FIREBASE_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
|[`list`](releases/list.md)|List releases for the specified project and application from Firebase API|
