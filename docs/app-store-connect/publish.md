
publish
=======


**Publish application packages to App Store, submit them to Testflight, and release to the groups of beta testers**
### Usage
```bash
app-store-connect publish [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--path APPLICATION_PACKAGE_PATH_PATTERNS]
    [--apple-id APPLE_ID]
    [--password APP_SPECIFIC_PASSWORD]
    [--testflight]
    [--locale LOCALE_DEFAULT]
    [--whats-new WHATS_NEW]
    [--beta-build-localizations BETA_BUILD_LOCALIZATIONS]
    [--beta-group BETA_GROUP_NAMES_OPTIONAL]
    [--skip-package-validation]
    [--max-build-processing-wait MAX_BUILD_PROCESSING_WAIT]
    [--altool-retries ALTOOL_RETRIES_COUNT]
    [--altool-retry-wait ALTOOL_RETRY_WAIT]
    [--altool-verbose-logging]
```
### Optional arguments for action `publish`

##### `--path=APPLICATION_PACKAGE_PATH_PATTERNS`


Path to artifact (\*.ipa or \*.pkg). Can be either a path literal, or a glob pattern to match projects in working directory. Multiple arguments. Default:&nbsp;`**/*.ipa, **/*.pkg`
##### `--apple-id, -u=APPLE_ID`


App Store Connect username used for application package validation and upload if App Store Connect API key is not specified
##### `--password, -p=APP_SPECIFIC_PASSWORD`


App-specific password used for application package validation and upload if App Store Connect API Key is not specified. Used together with --apple-id and should match pattern `abcd-abcd-abcd-abcd`. Create an app-specific password in the Security section of your Apple ID account. Learn more from https://support.apple.com/en-us/HT204397. If not given, the value will be checked from the environment variable `APP_SPECIFIC_PASSWORD`. Alternatively to entering `APP_SPECIFIC_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--testflight, -t`


Submit an app for Testflight beta app review to allow external testing
##### `--locale, -l=da | de-DE | el | en-AU | en-CA | en-GB | en-US | es-ES | es-MX | fi | fr-CA | fr-FR | id | it | ja | ko | ms | nl-NL | no | pt-BR | pt-PT | ru | sv | th | tr | vi | zh-Hans | zh-Hant`


The locale code name for displaying localized "What's new" content in TestFlight. In case not provided, application's primary locale from test information is used instead. Learn more from https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalizationcreaterequest/data/attributes
##### `--whats-new, -n=WHATS_NEW`


Describe the changes and additions to the build and indicate the features you would like your users to tests. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_WHATS_NEW`. Alternatively to entering `WHATS_NEW` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--beta-build-localizations=BETA_BUILD_LOCALIZATIONS`


Localized beta test info for what's new in the uploaded build as a JSON encoded list. For example, `[{"locale": "en-US", "whats_new": "What's new in English"}]`. See `--locale` for possible locale options. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_BETA_BUILD_LOCALIZATIONS`. Alternatively to entering `BETA_BUILD_LOCALIZATIONS` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--beta-group=BETA_GROUP_NAMES_OPTIONAL`


Name of your Beta group. Multiple arguments
##### `--skip-package-validation`


Skip package validation before uploading it to App Store Connect. Use this switch to opt out from running `altool --validate-app` before uploading package to App Store connect. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_SKIP_PACKAGE_VALIDATION`.
##### `--max-build-processing-wait=MAX_BUILD_PROCESSING_WAIT`


Maximum amount of minutes to wait for the freshly uploaded build to be processed by Apple and retry submitting the build for beta review. If the processing is not finished within the specified timeframe, further submission will be terminated. Waiting will be skipped if the value is set to 0, further actions might fail if the build is not processed yet. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_MAX_BUILD_PROCESSING_WAIT`. [Default: 20]
##### `--altool-retries=ALTOOL_RETRIES_COUNT`


How many times should the package validation or upload action attempted in case it failed due to known `altool` issue (authentication failure or request timeout). If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_RETRIES`. [Default: 10]
##### `--altool-retry-wait=ALTOOL_RETRY_WAIT`


For how long (in seconds) should the tool wait between the retries of package validation or upload actions in case they failed due to known `altool` issues (authentication failure or request timeout). See also --altool-retries for more configuration options. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_RETRY_WAIT`. [Default: 0.5]
##### `--altool-verbose-logging`


Show verbose log output when launching Application Loader tool. That is add `--verbose` flag to `altool` invocations when either validating the package, or while uploading the pakcage to App Store Connect. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_VERBOSE_LOGGING`.
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