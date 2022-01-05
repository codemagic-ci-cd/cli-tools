
list
====


**Find and list apps added in App Store Connect**
### Usage
```bash
app-store-connect apps list [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--api-unauthorized-retries UNAUTHORIZED_REQUEST_RETRIES]
    [--disable-jwt-cache]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--bundle-id-identifier BUNDLE_ID_IDENTIFIER_OPTIONAL]
    [--strict-match-identifier]
    [--app-id APPLICATION_ID_RESOURCE_ID_OPTIONAL]
    [--app-name APPLICATION_NAME]
    [--app-sku APPLICATION_SKU]
    [--version-string VERSION_STRING]
    [--platform PLATFORM_OPTIONAL]
    [--state APP_STORE_STATE]
```
### Optional arguments for action `list`

##### `--bundle-id-identifier=BUNDLE_ID_IDENTIFIER_OPTIONAL`


Identifier of the Bundle ID. For example `com.example.app`
##### `--strict-match-identifier`


Only match Bundle IDs that have exactly the same identifier specified by `BUNDLE_ID_IDENTIFIER`. By default identifier `com.example.app` also matches Bundle IDs with identifier such as `com.example.app.extension`
##### `--app-id, --application-id=APPLICATION_ID_RESOURCE_ID_OPTIONAL`


Application Apple ID. An automatically generated ID assigned to your app
##### `--app-name, --application-name=APPLICATION_NAME`


The name of your app as it will appear in the App Store
##### `--app-sku, --application-sku=APPLICATION_SKU`


A unique ID for your app that is not visible on the App Store.
##### `--version-string, --app-store-version=VERSION_STRING`


Version of the build published to App Store that identifies an iteration of the bundle. The string can only contain one to three groups of numeric characters (0-9) separated by period in the format [Major].[Minor].[Patch]. For example `3.2.46`
##### `--platform, --app-store-version-platform=IOS | MAC_OS | TV_OS`


App Store Version platform
##### `--state, --app-store-version-state=DEVELOPER_REMOVED_FROM_SALE | DEVELOPER_REJECTED | IN_REVIEW | INVALID_BINARY | METADATA_REJECTED | PENDING_APPLE_RELEASE | PENDING_CONTRACT | PENDING_DEVELOPER_RELEASE | PREPARE_FOR_SUBMISSION | PREORDER_READY_FOR_SALE | PROCESSING_FOR_APP_STORE | READY_FOR_SALE | REJECTED | REMOVED_FROM_SALE | WAITING_FOR_EXPORT_COMPLIANCE | WAITING_FOR_REVIEW | REPLACED_WITH_NEW_VERSION`


State of App Store Version
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


App Store Connect API private key used for JWT authentication to communicate with Apple services. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not provided, the key will be searched from the following directories in sequence for a private key file with the name `AuthKey_<key_identifier>.p8`: private_keys, ~/private_keys, ~/.private_keys, ~/.appstoreconnect/private_keys, where <key_identifier> is the value of `--key-id`. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering `PRIVATE_KEY` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
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