
delete_bundle_id
================
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``app-store-connect delete-bundle-id [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--ignore-not-found] BUNDLE_ID_RESOURCE_ID``
#### Delete specified Bundle ID from Apple Developer portal.

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

### Required arguments for command delete_bundle_id

|Argument|Description|Type|
| :--- | :--- | :--- |
|BUNDLE_ID_RESOURCE_ID|Alphanumeric ID value of the Bundle ID|ResourceId|

### Optional arguments for command delete_bundle_id

|Flags|Description|Type|
| :--- | :--- | :--- |
|--ignore-not-found|Do not raise exceptions if the specified resource does not exist.|bool|

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
