
google-play
===========


**Utility to get the latest build numbers from Google Play using Google Play Developer API**
### Usage
```bash
google-play [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials GCLOUD_SERVICE_ACCOUNT_CREDENTIALS]
    ACTION
```
### Optional arguments for command `google-play`

##### `--credentials=GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`


Gcloud service account credentials with the `JSON` key type to access Google Play Developer API. If not given, the value will be checked from the environment variable `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
|[`get-latest-build-number`](get-latest-build-number.md)|Get latest build number from Google Play Developer API matching given constraints|

### Action groups

|Action group|Description|
| :--- | :--- |
|[`tracks`](tracks.md)|Manage your Google Play release tracks|
