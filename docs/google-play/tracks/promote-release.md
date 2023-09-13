
promote-release
===============


**Promote releases from source track to target track. If filters for source         track release are not specified, then the latest release will be promoted**
### Usage
```bash
google-play tracks promote-release [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials GCLOUD_SERVICE_ACCOUNT_CREDENTIALS]
    [--release-status PROMOTED_STATUS]
    [--user-fraction PROMOTED_USER_FRACTION]
    [--version-code-filter PROMOTE_VERSION_CODE]
    [--release-status-filter PROMOTE_STATUS]
    [--json]
    --package-name PACKAGE_NAME
    --source-track SOURCE_TRACK_NAME
    --target-track TARGET_TRACK_NAME
```
### Required arguments for action `promote-release`

##### `--package-name, -p=PACKAGE_NAME`


Package name of the app in Google Play Console. For example `com.example.app`
##### `--source-track=SOURCE_TRACK_NAME`


Name of the track from where releases are promoted from. For example `internal`
##### `--target-track=TARGET_TRACK_NAME`


Name of the track to which releases are promoted to. For example `alpha`
### Optional arguments for action `promote-release`

##### `--release-status=statusUnspecified | draft | inProgress | halted | completed`


Promoted release status in the target track. Default:&nbsp;`completed`
##### `--user-fraction=PROMOTED_USER_FRACTION`


Fraction of users who are eligible for a staged promoted release in the target track. Number from interval `0 < fraction < 1`. Can only be set when status is `inProgress` or `halted`
##### `--version-code-filter=PROMOTE_VERSION_CODE`


Promote only release from source track that contains specified version code
##### `--release-status-filter=statusUnspecified | draft | inProgress | halted | completed`


Promote only release from source track with specified status
##### `--json, -j`


Whether to show the request response in JSON format
### Optional arguments for command `google-play`

##### `--credentials=GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`


Gcloud service account credentials with `JSON` key type to access Google Play Developer API. If not given, the value will be checked from the environment variable `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS`. Alternatively to entering CREDENTIALS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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
