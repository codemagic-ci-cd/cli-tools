
fetch-signing-files
===================


**Fetch provisioning profiles and code signing certificates         for Bundle ID with given identifier**
### Usage
```bash
app-store-connect fetch-signing-files [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--platform PLATFORM]
    [--certificate-key PRIVATE_KEY]
    [--certificate-key-password PRIVATE_KEY_PASSWORD]
    [--p12-password P12_CONTAINER_PASSWORD]
    [--type PROFILE_TYPE]
    [--strict-match-identifier]
    [--create]
    BUNDLE_ID_IDENTIFIER
```
### Required arguments for action `fetch-signing-files`

##### `BUNDLE_ID_IDENTIFIER`


Identifier of the Bundle ID. For example `com.example.app`
### Optional arguments for action `fetch-signing-files`

##### `--platform=IOS | MAC_OS | UNIVERSAL | SERVICES`


Bundle ID platform. Default:&nbsp;`IOS`
##### `--certificate-key=PRIVATE_KEY`


Private key used to generate the certificate. Used together with --save or --create options. If not given, the value will be checked from environment variable `CERTIFICATE_PRIVATE_KEY`. Alternatively to entering CERTIFICATE_KEY in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--certificate-key-password=PRIVATE_KEY_PASSWORD`


Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted. If not given, the value will be checked from environment variable `CERTIFICATE_PRIVATE_KEY_PASSWORD`. Alternatively to entering CERTIFICATE_KEY_PASSWORD in plaintext, it may also be specified using a `@env:` prefix followed by a environment variable name, or `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from file at `<file_path>`.
##### `--p12-password=P12_CONTAINER_PASSWORD`


If provided, the saved p12 container will be encrypted using this password. Used together with --save option.
##### `--type=IOS_APP_ADHOC | IOS_APP_DEVELOPMENT | IOS_APP_INHOUSE | IOS_APP_STORE | MAC_APP_DEVELOPMENT | MAC_APP_DIRECT | MAC_APP_STORE | MAC_CATALYST_APP_DEVELOPMENT | MAC_CATALYST_APP_DIRECT | MAC_CATALYST_APP_STORE | TVOS_APP_ADHOC | TVOS_APP_DEVELOPMENT | TVOS_APP_INHOUSE | TVOS_APP_STORE`


Type of the provisioning profile. Default:&nbsp;`IOS_APP_DEVELOPMENT`
##### `--strict-match-identifier`


Only match Bundle IDs that have exactly the same identifier specified by `BUNDLE_ID_IDENTIFIER`. By default identifier `com.example.app` also matches Bundle IDs with identifier such as `com.example.app.extension`
##### `--create`


Whether to create the resource if it does not exist yet
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