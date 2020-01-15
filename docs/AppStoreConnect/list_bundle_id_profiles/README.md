
list_bundle_id_profiles
=======================

#### List provisioning profiles from Apple Developer Portal for specified Bundle IDs.

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

### Required arguments for command list_bundle_id_profiles

|Flags|Argument|Description|Type|Multiple arguments|
| :--- | :--- | :--- | :--- | :--- |
|--bundle-ids|BUNDLE_ID_RESOURCE_IDS|Alphanumeric ID value of the Bundle ID|ResourceId|Yes|

### Optional arguments for command list_bundle_id_profiles

|Flags|Argument|Description|Type|Choices|
| :--- | :--- | :--- | :--- | :--- |
|--type|PROFILE_TYPE_OPTIONAL|Type of the provisioning profile|ProfileType|IOS_APP_ADHOC <br />IOS_APP_DEVELOPMENT <br />IOS_APP_INHOUSE <br />IOS_APP_STORE <br />MAC_APP_DEVELOPMENT <br />MAC_APP_DIRECT <br />MAC_APP_STORE <br />TVOS_APP_ADHOC <br />TVOS_APP_DEVELOPMENT <br />TVOS_APP_INHOUSE <br />TVOS_APP_STORE|
|--state|PROFILE_STATE_OPTIONAL|State of the provisioning profile|ProfileState|ACTIVE <br />INVALID|
|--name|PROFILE_NAME|Name of the provisioning profile|str||
|--save|SAVE|Whether to save the resources to disk. See [36mPROFILES_DIRECTORY[0m and [36mCERTIFICATES_DIRECTORY[0m for more information.|bool||

### Optional arguments for AppStoreConnect

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--log-api-calls|LOG_REQUESTS|Turn on logging for App Store Connect API HTTP requests|bool||
|--json|JSON_OUTPUT|Whether to show the resource in JSON format|bool||
|--issuer-id|ISSUER_ID|App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|IssuerIdArgument||
|--key-id|KEY_IDENTIFIER|App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|KeyIdentifierArgument||
|--private-key|PRIVATE_KEY|App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|PrivateKeyArgument||
|--certificates-dir|CERTIFICATES_DIRECTORY|Directory where the code signing certificates will be saved|Path|/Users/stas/Library/MobileDevice/Certificates|
|--profiles-dir|PROFILES_DIRECTORY|Directory where the provisioning profiles will be saved|Path|/Users/stas/Library/MobileDevice/Provisioning Profiles|
