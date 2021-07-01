
beta-build-localizations
========================


**Manage your beta builds localizations in App Store Connect**
### Usage
```bash
app-store-connect beta-build-localizations [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    ACTION
```
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--json`


Whether to show the resource in JSON format
##### `--issuer-id=ISSUER_ID`


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ISSUER_ID`. Alternatively to entering `ISSUER_ID` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_KEY_IDENTIFIER`. Alternatively to entering `KEY_IDENTIFIER` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key used for JWT authentication to communicate with Apple services. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not provided, the key will be searched from the following directories in sequence for a private key file with the name `AuthKey_<key_identifier>.p8`: private_keys, ~/private_keys, ~/.private_keys, ~/.appstoreconnect/private_keys, where <key_identifier> is the value of --key-id. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering `PRIVATE_KEY` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
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
### Actions

|Action|Description|
| :--- | :--- |
|[`create`](beta-build-localizations/create.md)|Create a beta build localization if it doesn't exist or update existing         beta build localization for specified locale|
|[`delete`](beta-build-localizations/delete.md)|Delete a beta build localization|
|[`get`](beta-build-localizations/get.md)|Get beta build localization|
|[`list`](beta-build-localizations/list.md)|List beta build localizations|
|[`modify`](beta-build-localizations/modify.md)|Update a beta build localization|
