
app-store-connect
=================


**Utility to download code signing certificates and provisioning profiles    from Apple Developer Portal using App Store Connect API to perform iOS code signing.**
### Usage
```bash
app-store-connect [-h] [-s] [-v] [--no-color] [--log-stream STREAM]
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


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
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


Log output stream. Default: stderr
### Actions

|Action|Description|
| :--- | :--- |
|[`create‑bundle‑id`](create‑bundle‑id.md)|Create Bundle ID in Apple Developer portal for specifier identifier.|
|[`create‑certificate`](create‑certificate.md)|Create code signing certificates of given type|
|[`create‑profile`](create‑profile.md)|Create provisioning profile of given type|
|[`delete‑bundle‑id`](delete‑bundle‑id.md)|Delete specified Bundle ID from Apple Developer portal.|
|[`delete‑certificate`](delete‑certificate.md)|Delete specified Signing Certificate from Apple Developer portal.|
|[`delete‑profile`](delete‑profile.md)|Delete specified Profile from Apple Developer portal.|
|[`fetch‑signing‑files`](fetch‑signing‑files.md)|Fetch provisioning profiles and code signing certificates        for Bundle ID with given identifier.|
|[`get‑bundle‑id`](get‑bundle‑id.md)|Get specified Bundle ID from Apple Developer portal.|
|[`get‑certificate`](get‑certificate.md)|Get specified Signing Certificate from Apple Developer portal.|
|[`get‑profile`](get‑profile.md)|Get specified Profile from Apple Developer portal.|
|[`list‑bundle‑id‑profiles`](list‑bundle‑id‑profiles.md)|List provisioning profiles from Apple Developer Portal for specified Bundle IDs.|
|[`list‑bundle‑ids`](list‑bundle‑ids.md)|List Bundle IDs from Apple Developer portal matching given constraints.|
|[`list‑certificates`](list‑certificates.md)|List Signing Certificates from Apple Developer Portal matching given constraints.|
|[`list‑devices`](list‑devices.md)|List Devices from Apple Developer portal matching given constraints.|
|[`list‑profiles`](list‑profiles.md)|List Profiles from Apple Developer portal matching given constraints.|
