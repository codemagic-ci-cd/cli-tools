
create
======


**Create an App Store Version Localization.         Add localized version-level information for a new locale.**
### Usage
```bash
app-store-connect app-store-version-localizations create [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--api-unauthorized-retries UNAUTHORIZED_REQUEST_RETRIES]
    [--api-server-error-retries SERVER_ERROR_RETRIES]
    [--disable-jwt-cache]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--description DESCRIPTION]
    [--keywords KEYWORDS]
    [--marketing-url MARKETING_URL]
    [--promotional-text PROMOTIONAL_TEXT]
    [--support-url SUPPORT_URL]
    [--whats-new WHATS_NEW]
    APP_STORE_VERSION_ID
    LOCALE
```
### Required arguments for action `create`

##### `APP_STORE_VERSION_ID`


UUID value of the App Store Version
##### `LOCALE`


The locale code name for App Store metadata in different languages. See available locale code names from https://developer.apple.com/documentation/appstoreconnectapi/betabuildlocalizationcreaterequest/data/attributes
### Optional arguments for action `create`

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
##### `--whats-new, -n=WHATS_NEW`


Describe what's new in this version of your app, such as new features, improvements, and bug fixes. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_WHATS_NEW`. Alternatively to entering `WHATS_NEW` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--api-unauthorized-retries, -r=UNAUTHORIZED_REQUEST_RETRIES`


Specify how many times the App Store Connect API request should be retried in case the called request fails due to an authentication error (401 Unauthorized response from the server). In case of the above authentication error, the request is retried usinga new JSON Web Token as many times until the number of retries is exhausted. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_API_UNAUTHORIZED_RETRIES`. [Default: 3]
##### `--api-server-error-retries=SERVER_ERROR_RETRIES`


Specify how many times the App Store Connect API request should be retried in case the called request fails due to a server error (response with status code 5xx). In case of server error, the request is retried until the number of retries is exhausted. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_API_SERVER_ERROR_RETRIES`. [Default: 3]
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
