
publish
=======


**Publish application packages to App Store and submit them to Testflight**
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
    [-u APPLE_ID]
    [-p APP_SPECIFIC_PASSWORD]
    [-t]
    [--locale LOCALE_OPTIONAL]
    [--whats-new WHATS_NEW]
    [--skip-package-validation]
```
### Optional arguments for action `publish`

##### `--path=APPLICATION_PACKAGE_PATH_PATTERNS`


Path to artifact (\*.ipa or \*.pkg). Can be either a path literal, or a glob pattern to match projects in working directory. Multiple arguments. Default:&nbsp;`**/*.ipa, **/*.pkg`
##### `-u, --apple-id=APPLE_ID`


App Store Connect username used for application package validation and upload if App Store Connect API key is not specified
##### `-p, --password=APP_SPECIFIC_PASSWORD`


App-specific password used for application package validation and upload if App Store Connect API Key is not specified. Used together with --apple-id and should match pattern `abcd-abcd-abcd-abcd`. Create an app-specific password in the Security section of your Apple ID account. Learn more from https://support.apple.com/en-us/HT204397. If not given, the value will be checked from environment variable `APP_SPECIFIC_PASSWORD`. Alternatively to entering` APP_SPECIFIC_PASSWORD `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `-t, --testflight`


Submit an app for Testflight beta app review to allow external testing
##### `--locale=da | de-DE | el | en-AU | en-CA | en-GB | en-US | es-ES | es-MX | fi | fr-CA | fr-FR | id | it | ja | ko | ms | nl-NL | no | pt-BR | pt-PT | ru | sv | th | tr | vi | zh-Hans | zh-Hant`


The specified locale, e.g. de-DE or en-GB
##### `--whats-new=WHATS_NEW`


A field that describes changes and additions to a build and indicates features you would like your users to test. If not given, the value will be checked from environment variable `WHATS_NEW`. Alternatively to entering` WHATS_NEW `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--skip-package-validation`


Skip package validation before uploading it to App Store Connect. Use this switch to opt out from running `altool --validate-app` before uploading package to App Store connect. If not given, the value will be checked from environment variable `APP_STORE_CONNECT_SKIP_PACKAGE_VALIDATION`.
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--json`


Whether to show the resource in JSON format
##### `--issuer-id=ISSUER_ID`


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from environment variable `APP_STORE_CONNECT_ISSUER_ID`. Alternatively to entering` ISSUER_ID `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from environment variable `APP_STORE_CONNECT_KEY_IDENTIFIER`. Alternatively to entering` KEY_IDENTIFIER `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key used for JWT authentication to communicate with Apple services. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not provided, the key will be searched from the following directories in sequence for a private key file with the name `AuthKey_<key_identifier>.p8`: private_keys, ~/private_keys, ~/.private_keys, ~/.appstoreconnect/private_keys, where <key_identifier> is the value of --key-id. If not given, the value will be checked from environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering` PRIVATE_KEY `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
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