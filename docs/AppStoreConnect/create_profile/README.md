
create_profile
==============


``app-store-connect create-profile [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--type {IOS_APP_ADHOC, IOS_APP_DEVELOPMENT, IOS_APP_INHOUSE, IOS_APP_STORE, MAC_APP_DEVELOPMENT, MAC_APP_DIRECT, MAC_APP_STORE, TVOS_APP_ADHOC, TVOS_APP_DEVELOPMENT, TVOS_APP_INHOUSE, TVOS_APP_STORE}] [--name PROFILE_NAME] [--save] BUNDLE_ID_RESOURCE_ID [--certificate-ids CERTIFICATE_RESOURCE_IDS] [--device-ids DEVICE_RESOURCE_IDS]``
#### Create provisioning profile of given type

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

### Required arguments for command create_profile

|Flags|Argument|Description|Type|Multiple arguments|
| :--- | :--- | :--- | :--- | :--- |
||BUNDLE_ID_RESOURCE_ID|Alphanumeric ID value of the Bundle ID|ResourceId||
|--certificate-ids|CERTIFICATE_RESOURCE_IDS|Alphanumeric ID value of the Signing Certificate|ResourceId|Yes|
|--device-ids|DEVICE_RESOURCE_IDS|Alphanumeric ID value of the Device|ResourceId|Yes|

### Optional arguments for command create_profile

|Flags|Argument|Description|Type|Default|Choices|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--type|PROFILE_TYPE|Type of the provisioning profile|ProfileType|IOS_APP_DEVELOPMENT|IOS_APP_ADHOC, IOS_APP_DEVELOPMENT, IOS_APP_INHOUSE, IOS_APP_STORE, MAC_APP_DEVELOPMENT, MAC_APP_DIRECT, MAC_APP_STORE, TVOS_APP_ADHOC, TVOS_APP_DEVELOPMENT, TVOS_APP_INHOUSE, TVOS_APP_STORE|
|--name|PROFILE_NAME|Name of the provisioning profile|str|||
|--save||Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.|bool|||

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
