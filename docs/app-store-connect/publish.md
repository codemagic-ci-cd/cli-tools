
publish
=======


**Publish application packages to App Store, submit them to Testflight, and release to the groups of beta testers**
### Usage
```bash
app-store-connect publish [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--api-unauthorized-retries UNAUTHORIZED_REQUEST_RETRIES]
    [--disable-jwt-cache]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--path APPLICATION_PACKAGE_PATH_PATTERNS]
    [--apple-id APPLE_ID]
    [--password APP_SPECIFIC_PASSWORD]
    [--enable-package-validation]
    [--skip-package-validation]
    [--skip-package-upload]
    [--max-build-processing-wait MAX_BUILD_PROCESSING_WAIT]
    [--beta-build-localizations BETA_BUILD_LOCALIZATIONS]
    [--testflight]
    [--beta-group BETA_GROUP_NAMES_OPTIONAL]
    [--app-store]
    [--platform PLATFORM_OPTIONAL]
    [--app-store-version-info APP_STORE_VERSION_INFO]
    [--copyright COPYRIGHT]
    [--earliest-release-date EARLIEST_RELEASE_DATE]
    [--release-type RELEASE_TYPE]
    [--version-string VERSION_STRING]
    [--description DESCRIPTION]
    [--keywords KEYWORDS]
    [--marketing-url MARKETING_URL]
    [--promotional-text PROMOTIONAL_TEXT]
    [--support-url SUPPORT_URL]
    [--app-store-version-localizations APP_STORE_VERSION_LOCALIZATION_INFOS]
    [--locale LOCALE_DEFAULT]
    [--whats-new WHATS_NEW]
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
##### `--enable-package-validation, -ev`


Validate package before uploading it to App Store Connect. Use this switch to enable running `altool --validate-app` before uploading the package to App Store connect. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ENABLE_PACKAGE_VALIDATION`.
##### `--skip-package-validation, -sv`


Deprecated. Starting from version `0.14.0` package validation before uploading it to App Store Connect is disabled by default. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_SKIP_PACKAGE_VALIDATION`.
##### `--skip-package-upload, -su`


Skip package upload before doing any other TestFlight or App Store related actions. Using this switch will opt out from running `altool --upload-app` as part of publishing action. Use this option in case your application package is already uploaded to App Store. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_SKIP_PACKAGE_UPLOAD`.
##### `--max-build-processing-wait, -w=MAX_BUILD_PROCESSING_WAIT`


Maximum amount of minutes to wait for the freshly uploaded build to be processed by Apple and retry submitting the build for (beta) review. Works in conjunction with TestFlight beta review submission, or App Store review submission and operations that depend on either one of those. If the processing is not finished within the specified timeframe, further submission will be terminated. Waiting will be skipped if the value is set to 0, further actions might fail if the build is not processed yet. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_MAX_BUILD_PROCESSING_WAIT`. [Default: 20]
### Optional arguments to add localized What's new (what to test) information to uploaded build

##### `--beta-build-localizations=BETA_BUILD_LOCALIZATIONS`


Localized beta test info for what's new in the uploaded build as a JSON encoded list. For example, `[{"locale": "en-US", "whats_new": "What's new in English"}]`. See `--locale` for possible locale options. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_BETA_BUILD_LOCALIZATIONS`. Alternatively to entering `BETA_BUILD_LOCALIZATIONS` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
### Optional arguments to submit build to TestFlight for beta review

##### `--testflight, -t`


Enable submission of an app for Testflight beta app review to allow external testing.
### Optional arguments to add build to Beta groups

##### `--beta-group=BETA_GROUP_NAMES_OPTIONAL`


Name of your Beta group. Multiple arguments
### Optional arguments to submit build to App Store review

##### `--app-store, -a`


Enable submission of an app to App Store app review procedure.
##### `--platform, --app-store-version-platform=IOS | MAC_OS | TV_OS`


App Store Version platform
##### `--app-store-version-info, -vi=APP_STORE_VERSION_INFO`


General App information and version release options for App Store version submission as a JSON encoded object. Alternative to individually defining `--platform`, `--copyright`, `--earliest-release-date`, `--release-type` and `--version-string`. For example, `{"platform": "IOS", "copyright": "2008 Acme Inc.", "version_string": "1.0.8", "release_type": "SCHEDULED", "earliest_release_date": "2021-11-10T14:00:00+00:00"}`. Definitions from the JSON will be overridden by dedicated CLI options if provided. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_APP_STORE_VERSION_INFO`. Alternatively to entering `APP_STORE_VERSION_INFO` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--copyright=COPYRIGHT`


The name of the person or entity that owns the exclusive rights to your app, preceded by the year the rights were obtained (for example, `2008 Acme Inc.`). Do not provide a URL.
##### `--earliest-release-date=EARLIEST_RELEASE_DATE`


Specify earliest return date for scheduled release type (see `--release-type` configuration option). Timezone aware ISO8601 timestamp with hour precision, for example `2021-11-10T14:00:00+00:00`.
##### `--release-type=MANUAL | AFTER_APPROVAL | SCHEDULED`


Choose when to release the app. You can either manually release the app at a later date on the App Store Connect website, or the app version can be automatically released right after it has been approved by App Review.
##### `--version-string, --app-store-version=VERSION_STRING`


Version of the build published to App Store that identifies an iteration of the bundle. The string can only contain one to three groups of numeric characters (0-9) separated by period in the format [Major].[Minor].[Patch]. For example `3.2.46`
##### `--description, -d=DESCRIPTION`


A description of your app, detailing features and functionality.
##### `--keywords, -k=KEYWORDS`


Include one or more keywords that describe your app. Keywords make App Store search results more accurate. Separate keywords with an English comma, Chinese comma, or a mix of both.
##### `--marketing-url=MARKETING_URL`


A URL with marketing information about your app. This URL will be visible on the App Store.
##### `--promotional-text=PROMOTIONAL_TEXT`


Promotional text lets you inform your App Store visitors of any current app features without requiring an updated submission. This text will appear above your description on the App Store for customers with devices running iOS 11 or later, and macOS 10.13 or later.
##### `--support-url=SUPPORT_URL`


A URL with support information for your app. This URL will be visible on the App Store.
##### `--app-store-version-localizations, -vl=APP_STORE_VERSION_LOCALIZATION_INFOS`


Localized App Store version meta information for App Store version submission as a JSON encoded list. Alternative to individually defining version release notes and other options via dedicated CLI options such as `--whats-new`. Definitions for duplicate locales are not allowed. For example, `[{"description": "App description", "keywords": "keyword, other keyword", "locale": "en-US", "marketing_url": "https://example.com", "promotional_text": "Promotional text", "support_url": "https://example.com", "whats_new": "Fixes an issue .."}]`. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_APP_STORE_VERSION_LOCALIZATIONS`. Alternatively to entering APP_STORE_VERSION_LOCALIZATIONS in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
### Optional arguments to add localized meta information about build for TestFlight or App Store review submission

##### `--locale, -l=da | de-DE | el | en-AU | en-CA | en-GB | en-US | es-ES | es-MX | fi | fr-CA | fr-FR | id | it | ja | ko | ms | nl-NL | no | pt-BR | pt-PT | ru | sv | th | tr | vi | zh-Hans | zh-Hant`


The locale code name for App Store metadata in different languages, or for displaying localized "What's new" content in TestFlight. In case not provided, application's primary locale is used instead. Learn more from https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalizationcreaterequest/data/attributes
##### `--whats-new, -n=WHATS_NEW`


Release notes either for TestFlight or App Store review submission. Describe what's new in this version of your app, such as new features, improvements, and bug fixes. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_WHATS_NEW`. Alternatively to entering `WHATS_NEW` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
### Optional arguments to set Apple's altool configuration options

##### `--altool-retries=ALTOOL_RETRIES_COUNT`


Define how many times should the package validation or upload action be attempted in case it failed due to a known `altool` issue (authentication failure or request timeout). If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_RETRIES`. [Default: 10]
##### `--altool-retry-wait=ALTOOL_RETRY_WAIT`


For how long (in seconds) should the tool wait between the retries of package validation or upload action retries in case they failed due to a known `altool` issues (authentication failure or request timeout). See also --altool-retries for more configuration options. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_RETRY_WAIT`. [Default: 0.5]
##### `--altool-verbose-logging`


Show verbose log output when launching Application Loader tool. That is add `--verbose` flag to `altool` invocations when either validating the package, or while uploading the pakcage to App Store Connect. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ALTOOL_VERBOSE_LOGGING`.
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--api-unauthorized-retries, -r=UNAUTHORIZED_REQUEST_RETRIES`


Specify how many times the App Store Connect API request should be retried in case the called request fails due to an authentication error (401 Unauthorized response from the server). In case of the above authentication error, the request is retried usinga new JSON Web Token as many times until the number of retries is exhausted. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_API_UNAUTHORIZED_RETRIES`. [Default: 3]
##### `--disable-jwt-cache`


Turn off caching App Store Connect JSON Web Tokens to disk. By default generated tokens are cached to disk to be reused between separate processes, which can can reduce number of false positive authentication errors from App Store Connect API. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_DISABLE_JWT_CACHE`.
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