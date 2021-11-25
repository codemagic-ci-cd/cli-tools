
submit-to-app-store
===================


**Submit build to App Store review**
### Usage
```bash
app-store-connect builds submit-to-app-store [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--copyright COPYRIGHT]
    [--earliest-release-date EARLIEST_RELEASE_DATE]
    [--platform PLATFORM]
    [--release-type RELEASE_TYPE]
    [--version-string VERSION_STRING]
    [--max-build-processing-wait MAX_BUILD_PROCESSING_WAIT]
    BUILD_ID_RESOURCE_ID
```
### Required arguments for action `submit-to-app-store`

##### `BUILD_ID_RESOURCE_ID`


Alphanumeric ID value of the Build
### Optional arguments for action `submit-to-app-store`

##### `--copyright=COPYRIGHT`


The name of the person or entity that owns the exclusive rights to your app, preceded by the year the rights were obtained (for example, "2008 Acme Inc."). Do not provide a URL.
##### `--earliest-release-date=EARLIEST_RELEASE_DATE`


Specify earliest return date for scheduled release type (see `--release-type` configuration option). Timezone aware ISO8601 timestamp with hour precision, for example `2021-11-10T14:00:00+00:00`.
##### `--platform, --app-store-version-platform=IOS | MAC_OS | TV_OS`


App Store Version platform. Default:&nbsp;`IOS`
##### `--release-type=MANUAL | AFTER_APPROVAL | SCHEDULED`


Choose when to release the app. You can either manually release the app at a later date on the App Store Connect website, or the app version can be automatically released right after it has been approved by App Review.
##### `--version-string, --app-store-version=VERSION_STRING`


Version of the build published to App Store that identifies an iteration of the bundle. The string can only contain one to three groups of numeric characters (0-9) separated by period in the format [Major].[Minor].[Patch]. For example `3.2.46`
##### `--max-build-processing-wait, -w=MAX_BUILD_PROCESSING_WAIT`


Maximum amount of minutes to wait for the freshly uploaded build to be processed by Apple and retry submitting the build for (beta) review. Works in conjunction with TestFlight beta review submission, or App Store review submission and operations that depend on either one of those. If the processing is not finished within the specified timeframe, further submission will be terminated. Waiting will be skipped if the value is set to 0, further actions might fail if the build is not processed yet. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_MAX_BUILD_PROCESSING_WAIT`. [Default: 20]
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--json`


Whether to show the resource in JSON format
##### `--issuer-id=ISSUER_ID`


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ISSUER_ID`. Alternatively to entering `ISSUER_ID` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_KEY_IDENTIFIER`. Alternatively to entering `KEY_IDENTIFIER` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key used for JWT authentication to communicate with Apple services. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not provided, the key will be searched from the following directories in sequence for a private key file with the name `AuthKey_<key_identifier>.p8`: private_keys, ~/private_keys, ~/.private_keys, ~/.appstoreconnect/private_keys, where <key_identifier> is the value of --key-id. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering `PRIVATE_KEY` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--certificates-dir=CERTIFICATES_DIRECTORY`


Directory where the code signing certificates will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates`
##### `--profiles-dir=PROFILES_DIRECTORY`


Directory where the provisioning profiles will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles`
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