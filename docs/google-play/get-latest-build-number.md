
get-latest-build-number
=======================


**Get latest build number from Google Play matching given constraints**
### Usage
```bash
google-play get-latest-build-number [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS]
    [--json]
    [--tracks TRACKS | --include-uploaded-builds]
    --package-name PACKAGE_NAME
```
### Required arguments for action `get-latest-build-number`

##### `--package-name, -p=PACKAGE_NAME`


Package name of the app in Google Play Console. For example `com.example.app`
### Optional mutually exclusive arguments for action `get-latest-build-number`

##### `--tracks, -t=TRACKS`


Get the build number from the specified track(s). If not specified, the highest build number across all tracks is returned. Multiple arguments
##### `--include-uploaded-builds`


Also check the version codes of all App Bundles and APKs uploaded to Google Play, including the ones that are not assigned to any track (for example builds that were uploaded but never released). Useful for incrementing the build number when some uploaded builds are not published
### Optional arguments for command `google-play`

##### `--credentials=GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS`


Google Play service account credentials with JSON key type to access Google Play API. If not given, the value will be checked from the environment variable `GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--json, -j`


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
