
list_bundle_id_profiles
=======================
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``app-store-connect list-bundle-id-profiles [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--type {IOS_APP_ADHOC, IOS_APP_DEVELOPMENT, IOS_APP_INHOUSE, IOS_APP_STORE, MAC_APP_DEVELOPMENT, MAC_APP_DIRECT, MAC_APP_STORE, TVOS_APP_ADHOC, TVOS_APP_DEVELOPMENT, TVOS_APP_INHOUSE, TVOS_APP_STORE}] [--state {ACTIVE, INVALID}] [--name PROFILE_NAME] [--save] [--bundle-ids BUNDLE_ID_RESOURCE_IDS]``
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
|--type|PROFILE_TYPE_OPTIONAL|Type of the provisioning profile|ProfileType|IOS_APP_ADHOC, IOS_APP_DEVELOPMENT, IOS_APP_INHOUSE, IOS_APP_STORE, MAC_APP_DEVELOPMENT, MAC_APP_DIRECT, MAC_APP_STORE, TVOS_APP_ADHOC, TVOS_APP_DEVELOPMENT, TVOS_APP_INHOUSE, TVOS_APP_STORE|
|--state|PROFILE_STATE_OPTIONAL|State of the provisioning profile|ProfileState|ACTIVE, INVALID|
|--name|PROFILE_NAME|Name of the provisioning profile|str||
|--save||Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.|bool||

### Optional arguments for AppStoreConnect

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">--log-api-calls</span>||Turn on logging for App Store Connect API HTTP requests|bool||
|<span style="white-space: nowrap">--json</span>||Whether to show the resource in JSON format|bool||
|<span style="white-space: nowrap">--issuer-id</span>|ISSUER_ID|App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|IssuerIdArgument||
|<span style="white-space: nowrap">--key-id</span>|KEY_IDENTIFIER|App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|KeyIdentifierArgument||
|<span style="white-space: nowrap">--private-key</span>|PRIVATE_KEY|App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.|PrivateKeyArgument||
|<span style="white-space: nowrap">--certificates-dir</span>|CERTIFICATES_DIRECTORY|Directory where the code signing certificates will be saved|Path|$HOME/Library/MobileDevice/Certificates|
|<span style="white-space: nowrap">--profiles-dir</span>|PROFILES_DIRECTORY|Directory where the provisioning profiles will be saved|Path|$HOME/Library/MobileDevice/Provisioning Profiles|
