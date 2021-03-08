
get-latest-build-number
=======================


**Get latest build number from Google Play Developer API matching given constraints**
### Usage
```bash
google-play get-latest-build-number [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    --package-name PACKAGE_NAME
    [--credentials GCLOUD_SERVICE_ACCOUNT_CREDENTIALS]
    [--log-api-calls]
    [--json]
    [--tracks TRACKS]
```
### Optional arguments for action `get-latest-build-number`

##### `--tracks=internal | alpha | beta | production`


Get the build number from the specified track(s). If not specified, the highest build number across all tracks (internal, alpha, beta, production) is returned. Multiple arguments
### Required arguments for command `google-play`

##### `--package-name=PACKAGE_NAME`


Package name of the app in Google Play Console (Ex: com.google.example)
### Optional arguments for command `google-play`

##### `--credentials=GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`


Gcloud service account credentials with `JSON` key type to access Google Play Developer API. If not given, the value will be checked from environment variable `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--log-api-calls`


Turn on logging for Google Play Developer API requests
##### `--json`


Whether to show the request response in JSON format
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