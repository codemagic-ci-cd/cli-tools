
AppStoreConnect
===============

#### Utility to download code signing certificates and provisioning profiles    from Apple Developer Portal using App Store Connect API to perform iOS code signing.

### Optional arguments

|Flags|Description|
| :--- | :--- |
|-h, --help|show this help message and exit|

### Options

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### AppStoreConnect actions

|Action|Description|
| :--- | :--- |
|[create_bundle_id](create_bundle_id/README.md)|Create Bundle ID in Apple Developer portal for specifier identifier.|
|[create_certificate](create_certificate/README.md)|Create code signing certificates of given type|
|[create_profile](create_profile/README.md)|Create provisioning profile of given type|
|[delete_bundle_id](delete_bundle_id/README.md)|Delete specified Bundle ID from Apple Developer portal.|
|[delete_certificate](delete_certificate/README.md)|Delete specified Signing Certificate from Apple Developer portal.|
|[delete_profile](delete_profile/README.md)|Delete specified Profile from Apple Developer portal.|
|[fetch_signing_files](fetch_signing_files/README.md)|Fetch provisioning profiles and code signing certificates        for Bundle ID with given identifier.|
|[get_bundle_id](get_bundle_id/README.md)|Get specified Bundle ID from Apple Developer portal.|
|[get_certificate](get_certificate/README.md)|Get specified Signing Certificate from Apple Developer portal.|
|[get_profile](get_profile/README.md)|Get specified Profile from Apple Developer portal.|
|[list_bundle_id_profiles](list_bundle_id_profiles/README.md)|List provisioning profiles from Apple Developer Portal for specified Bundle IDs.|
|[list_bundle_ids](list_bundle_ids/README.md)|List Bundle IDs from Apple Developer portal matching given constraints.|
|[list_certificates](list_certificates/README.md)|List Signing Certificates from Apple Developer Portal matching given constraints.|
|[list_devices](list_devices/README.md)|List Devices from Apple Developer portal matching given constraints.|
|[list_profiles](list_profiles/README.md)|List Profiles from Apple Developer portal matching given constraints.|

### Optional arguments for AppStoreConnect

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--log-api-calls|LOG_REQUESTS|Turn on logging for App Store Connect API HTTP requests|bool||
|--json|JSON_OUTPUT|Whether to show the resource in JSON format|bool||
|--issuer-id|ISSUER_ID|App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|IssuerIdArgument||
|--key-id|KEY_IDENTIFIER|App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|KeyIdentifierArgument||
|--private-key|PRIVATE_KEY|App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|PrivateKeyArgument||
|--certificates-dir|CERTIFICATES_DIRECTORY|Directory where the code signing certificates will be saved|Path|$HOME/Library/MobileDevice/Certificates|
|--profiles-dir|PROFILES_DIRECTORY|Directory where the provisioning profiles will be saved|Path|$HOME/Library/MobileDevice/Provisioning Profiles|
