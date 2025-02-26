
publish
=======


**Publish APK at given path to Google Play as a release to specified track**
### Usage
```bash
google-play apks publish [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--credentials GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS]
    [--json]
    [--release-name RELEASE_NAME]
    [--in-app-update-priority IN_APP_UPDATE_PRIORITY]
    [--release-notes RELEASE_NOTES]
    [--changes-not-sent-for-review]
    [--proguard-mapping PROGUARD_MAPPING_PATH]
    [--main-expansion-file MAIN_EXPANSION_FILE_PATH]
    [--patch-expansion-file PATCH_EXPANSION_FILE_PATH]
    [--rollout-fraction STAGED_ROLLOUT_FRACTION | --draft]
    --apk APK_PATH
    --track TRACK_NAME
```
### Required arguments for action `publish`

##### `--apk, -a=APK_PATH`


Path to APK file (\*.apk)
##### `--track, -t=TRACK_NAME`


Release track name. For example `alpha` or `production`
### Optional arguments for action `publish`

##### `--release-name, -r=RELEASE_NAME`


Name of the release. Not required to be unique. If not set, the name is generated from the APK's or App Bundles `versionName`
##### `--in-app-update-priority, -i=IN_APP_UPDATE_PRIORITY`


Priority of the release. If your application supports in-app updates, set the release priority by specifying an integer in range [0, 5]
##### `--release-notes, -n=RELEASE_NOTES`


Localised release notes as a JSON encoded list to let users know what's in your release. For example, `[{"language": "en-US", "text": "What's new in English"}]`. If not given, the value will be checked from the environment variable `GOOGLE_PLAY_RELEASE_NOTES`. Alternatively to entering `RELEASE_NOTES` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--changes-not-sent-for-review`


Do not send changes for review. Indicates that the changes in this edit will not be reviewed until they are explicitly sent for review from the Google Play Console UI
##### `--proguard-mapping=PROGUARD_MAPPING_PATH`


Path to the ProGuard mapping deobfuscation file to be uploaded for the published APK
##### `--main-expansion-file=MAIN_EXPANSION_FILE_PATH`


Main expansion file to be uploaded for the published APK
##### `--patch-expansion-file=PATCH_EXPANSION_FILE_PATH`


Patch expansion file to be uploaded for the published APK
### Optional mutually exclusive arguments for action `publish`

##### `--rollout-fraction, -f=STAGED_ROLLOUT_FRACTION`


Staged rollout user fraction from range (0, 1). When you have a new version of your application that you want to gradually deploy, you may choose to release it as a "staged rollout" version. If you do this, Google Play automatically deploys it to the desired fraction of the app's users which you specify
##### `--draft, -d`


Indicates that the artifacts generated in the build will be uploaded to Google Play as a draft release.
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
