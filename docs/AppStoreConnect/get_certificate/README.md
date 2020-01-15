
get_certificate
===============

#### Get specified Signing Certificate from Apple Developer portal.

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

### Required arguments for command get_certificate

|Argument|Description|Type|
| :--- | :--- | :--- |
|CERTIFICATE_RESOURCE_ID|Alphanumeric ID value of the Signing Certificate|ResourceId|

### Optional arguments for command get_certificate

|Flags|Argument|Description|Type|
| :--- | :--- | :--- | :--- |
|--certificate-key|PRIVATE_KEY|Private key used to generate the certificate. Used together with [94m--save[0m or [94m--create[0m options.|CertificateKeyArgument|
|--certificate-key-password|PRIVATE_KEY_PASSWORD|Password of the private key used to generate the certificate. Used together with [94m--certificate-key[0m or [94m--certificate-key-path[0m options if the provided key is encrypted.|CertificateKeyPasswordArgument|
|--p12-password|P12_CONTAINER_PASSWORD|If provided, the saved p12 container will be encrypted using this password. Used together with [94m--save[0m option.|str|
|--save|SAVE|Whether to save the resources to disk. See [36mPROFILES_DIRECTORY[0m and [36mCERTIFICATES_DIRECTORY[0m for more information.|bool|

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
