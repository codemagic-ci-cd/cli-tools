
delete_certificate
==================

#### Delete specified Signing Certificate from Apple Developer portal.

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

### Required arguments for command delete_certificate

|Argument|Description|Type|
| :--- | :--- | :--- |
|CERTIFICATE_RESOURCE_ID|Alphanumeric ID value of the Signing Certificate|ResourceId|

### Optional arguments for command delete_certificate

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|--ignore-not-found|IGNORE_NOT_FOUND|Do not raise exceptions if the specified resource does not exist.|bool|

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
