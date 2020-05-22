
get‑bundle‑id
=============


**Get specified Bundle ID from Apple Developer portal.**
### Usage
```bash
app-store-connect get‑bundle‑id [-h] [-s] [-v] [--no-color] [--log-stream STREAM]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    BUNDLE_ID_RESOURCE_ID
```
### Required arguments for action `get‑bundle‑id`

##### `BUNDLE_ID_RESOURCE_ID`


Alphanumeric ID value of the Bundle ID
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


App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering` PRIVATE_KEY `in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--certificates-dir=CERTIFICATES_DIRECTORY`


Directory where the code signing certificates will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates`
##### `--profiles-dir=PROFILES_DIRECTORY`


Directory where the provisioning profiles will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles`
### Common options

##### `-h, --help`


show this help message and exit
##### `-s, --silent`


Disable log output for commands
##### `-v, --verbose`


Enable verbose logging for commands
##### `--no-color`


Do not use ANSI colors to format terminal output
##### `--log-stream=stderr | stdout`


Log output stream. Default `stderr`