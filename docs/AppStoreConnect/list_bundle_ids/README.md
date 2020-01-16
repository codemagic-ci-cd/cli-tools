
list_bundle_ids
===============


``app-store-connect list-bundle-ids [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--bundle-id-identifier BUNDLE_ID_IDENTIFIER_OPTIONAL] [--name BUNDLE_ID_NAME] [--platform {IOS, MAC_OS}] ``
#### List Bundle IDs from Apple Developer portal matching given constraints.

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

### Optional arguments for command list_bundle_ids

|Flags|Argument|Description|Type|Choices|
| :--- | :--- | :--- | :--- | :--- |
|--bundle-id-identifier|BUNDLE_ID_IDENTIFIER_OPTIONAL|Identifier of the Bundle ID|str||
|--name|BUNDLE_ID_NAME|Name of the Bundle ID. If the resource is being created, the default will be deduced from given Bundle ID identifier.|str||
|--platform|PLATFORM_OPTIONAL|Bundle ID platform|BundleIdPlatform|IOS, MAC_OS|

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
