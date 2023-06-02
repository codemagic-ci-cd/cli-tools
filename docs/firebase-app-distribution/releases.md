
releases
========


**Manage your Firebase application releases**
### Usage
```bash
firebase-app-distribution releases [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    --project-id PROJECT_ID
    [--credentials FIREBASE_SERVICE_ACCOUNT_CREDENTIALS]
    ACTION
```
### Required arguments for command `firebase-app-distribution`

##### `--project-id, -p=PROJECT_ID`


Project ID in Firebase. For example `228333310124`
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
### Actions

|Action|Description|
| :--- | :--- |
|[`list`](releases/list.md)|List releases for the Firebase application|
