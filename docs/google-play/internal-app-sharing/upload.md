
upload
======


**Upload APK or App Bundle to Google Play through Internal App Sharing to get a link that can be shared with your team**
### Usage
```bash
google-play internal-app-sharing upload [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS]
    [--json]
    (--apk APK_PATH_MUTUALLY_EXCLUSIVE | --bundle BUNDLE_PATH_MUTUALLY_EXCLUSIVE)
```
### Required mutually exclusive arguments for action `upload`

##### `--apk, -a=APK_PATH_MUTUALLY_EXCLUSIVE`


Path to APK file (\*.apk)
##### `--bundle, -b=BUNDLE_PATH_MUTUALLY_EXCLUSIVE`


Path to App Bundle file (\*.aab)
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
