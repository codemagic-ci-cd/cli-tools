
fetch_signing_files
===================

#### Fetch provisioning profiles and code signing certificates        for Bundle ID with given identifier.

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

### Required arguments for command fetch_signing_files

|Argument|Description|Type|
| :--- | :--- | :--- |
|BUNDLE_ID_IDENTIFIER|Identifier of the Bundle ID|str|

### Optional arguments for command fetch_signing_files

|Flags|Argument|Description|Type|Default|Choices|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--platform|PLATFORM|Bundle ID platform|BundleIdPlatform|IOS|IOS <br />MAC_OS|
|--certificate-key|PRIVATE_KEY|Private key used to generate the certificate. Used together with [94m--save[0m or [94m--create[0m options.|CertificateKeyArgument|||
|--certificate-key-password|PRIVATE_KEY_PASSWORD|Password of the private key used to generate the certificate. Used together with [94m--certificate-key[0m or [94m--certificate-key-path[0m options if the provided key is encrypted.|CertificateKeyPasswordArgument|||
|--p12-password|P12_CONTAINER_PASSWORD|If provided, the saved p12 container will be encrypted using this password. Used together with [94m--save[0m option.|str|||
|--type|PROFILE_TYPE|Type of the provisioning profile|ProfileType|IOS_APP_DEVELOPMENT|IOS_APP_ADHOC <br />IOS_APP_DEVELOPMENT <br />IOS_APP_INHOUSE <br />IOS_APP_STORE <br />MAC_APP_DEVELOPMENT <br />MAC_APP_DIRECT <br />MAC_APP_STORE <br />TVOS_APP_ADHOC <br />TVOS_APP_DEVELOPMENT <br />TVOS_APP_INHOUSE <br />TVOS_APP_STORE|
|--create|CREATE_RESOURCE|Whether to create the resource if it does not exist yet|bool|||

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
