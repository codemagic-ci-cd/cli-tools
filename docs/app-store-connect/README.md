
app-store-connect
=================


**Utility to download code signing certificates and provisioning profiles     from Apple Developer Portal using App Store Connect API to perform iOS code signing.**
### Usage
```bash
app-store-connect [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
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
|[<nobr><code>create-bundle-id</code></nobr>](create-bundle-id.md)|Create Bundle ID in Apple Developer portal for specifier identifier.|
|[<nobr><code>create-certificate</code></nobr>](create-certificate.md)|Create code signing certificates of given type|
|[<nobr><code>create-profile</code></nobr>](create-profile.md)|Create provisioning profile of given type|
|[<nobr><code>delete-bundle-id</code></nobr>](delete-bundle-id.md)|Delete specified Bundle ID from Apple Developer portal.|
|[<nobr><code>delete-certificate</code></nobr>](delete-certificate.md)|Delete specified Signing Certificate from Apple Developer portal.|
|[<nobr><code>delete-profile</code></nobr>](delete-profile.md)|Delete specified Profile from Apple Developer portal.|
|[<nobr><code>fetch-signing-files</code></nobr>](fetch-signing-files.md)|Fetch provisioning profiles and code signing certificates         for Bundle ID with given identifier.|
|[<nobr><code>get-bundle-id</code></nobr>](get-bundle-id.md)|Get specified Bundle ID from Apple Developer portal.|
|[<nobr><code>get-certificate</code></nobr>](get-certificate.md)|Get specified Signing Certificate from Apple Developer portal.|
|[<nobr><code>get-profile</code></nobr>](get-profile.md)|Get specified Profile from Apple Developer portal.|
|[<nobr><code>list-bundle-id-profiles</code></nobr>](list-bundle-id-profiles.md)|List provisioning profiles from Apple Developer Portal for specified Bundle IDs.|
|[<nobr><code>list-bundle-ids</code></nobr>](list-bundle-ids.md)|List Bundle IDs from Apple Developer portal matching given constraints.|
|[<nobr><code>list-certificates</code></nobr>](list-certificates.md)|List Signing Certificates from Apple Developer Portal matching given constraints.|
|[<nobr><code>list-devices</code></nobr>](list-devices.md)|List Devices from Apple Developer portal matching given constraints.|
|[<nobr><code>list-profiles</code></nobr>](list-profiles.md)|List Profiles from Apple Developer portal matching given constraints.|
