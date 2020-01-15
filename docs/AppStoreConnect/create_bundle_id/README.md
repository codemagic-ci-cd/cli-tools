
create_bundle_id
================

#### Create Bundle ID in Apple Developer portal for specifier identifier.

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

### Required arguments for command create_bundle_id

|Argument|Description|Type|
| :--- | :--- | :--- |
|BUNDLE_ID_IDENTIFIER|Identifier of the Bundle ID|str|

### Optional arguments for command create_bundle_id

|Flags|Argument|Description|Type|Default|Choices|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--name|BUNDLE_ID_NAME|Name of the Bundle ID. If the resource is being created, the default will be deduced from given Bundle ID identifier.|str|||
|--platform|PLATFORM|Bundle ID platform|BundleIdPlatform|IOS|IOS <br />MAC_OS|

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
