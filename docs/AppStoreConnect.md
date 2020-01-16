
AppStoreConnect
===============


``app-store-connect [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls ] [--json ] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] {create_bundle_id, create_certificate, create_profile, delete_bundle_id, delete_certificate, delete_profile, fetch_signing_files, get_bundle_id, get_certificate, get_profile, list_bundle_id_profiles, list_bundle_ids, list_certificates, list_devices, list_profiles}``
#### Utility to download code signing certificates and provisioning profiles    from Apple Developer Portal using App Store Connect API to perform iOS code signing.

### Optional arguments

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-h, --help|show this help message and exit||
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### AppStoreConnect actions

|Action|Description|
| :--- | :--- |
|[create_bundle_id](AppStoreConnect_create_bundle_id.md)|Create Bundle ID in Apple Developer portal for specifier identifier.|
|[create_certificate](AppStoreConnect_create_certificate.md)|Create code signing certificates of given type|
|[create_profile](AppStoreConnect_create_profile.md)|Create provisioning profile of given type|
|[delete_bundle_id](AppStoreConnect_delete_bundle_id.md)|Delete specified Bundle ID from Apple Developer portal.|
|[delete_certificate](AppStoreConnect_delete_certificate.md)|Delete specified Signing Certificate from Apple Developer portal.|
|[delete_profile](AppStoreConnect_delete_profile.md)|Delete specified Profile from Apple Developer portal.|
|[fetch_signing_files](AppStoreConnect_fetch_signing_files.md)|Fetch provisioning profiles and code signing certificates        for Bundle ID with given identifier.|
|[get_bundle_id](AppStoreConnect_get_bundle_id.md)|Get specified Bundle ID from Apple Developer portal.|
|[get_certificate](AppStoreConnect_get_certificate.md)|Get specified Signing Certificate from Apple Developer portal.|
|[get_profile](AppStoreConnect_get_profile.md)|Get specified Profile from Apple Developer portal.|
|[list_bundle_id_profiles](AppStoreConnect_list_bundle_id_profiles.md)|List provisioning profiles from Apple Developer Portal for specified Bundle IDs.|
|[list_bundle_ids](AppStoreConnect_list_bundle_ids.md)|List Bundle IDs from Apple Developer portal matching given constraints.|
|[list_certificates](AppStoreConnect_list_certificates.md)|List Signing Certificates from Apple Developer Portal matching given constraints.|
|[list_devices](AppStoreConnect_list_devices.md)|List Devices from Apple Developer portal matching given constraints.|
|[list_profiles](AppStoreConnect_list_profiles.md)|List Profiles from Apple Developer portal matching given constraints.|

### Optional arguments for AppStoreConnect

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--log-api-calls||Turn on logging for App Store Connect API HTTP requests|bool||
|--json||Whether to show the resource in JSON format|bool||
|--issuer-id|ISSUER_ID|App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|IssuerIdArgument||
|--key-id|KEY_IDENTIFIER|App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|KeyIdentifierArgument||
|--private-key|PRIVATE_KEY|App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|PrivateKeyArgument||
|--certificates-dir|CERTIFICATES_DIRECTORY|Directory where the code signing certificates will be saved|Path|$HOME/Library/MobileDevice/Certificates|
|--profiles-dir|PROFILES_DIRECTORY|Directory where the provisioning profiles will be saved|Path|$HOME/Library/MobileDevice/Provisioning Profiles|
