
list_certificates
=================

#### List Signing Certificates from Apple Developer Portal matching given constraints.

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

### Optional arguments for command list_certificates

|Flags|Argument|Description|Type|Choices|
| :--- | :--- | :--- | :--- | :--- |
|--type|CERTIFICATE_TYPE_OPTIONAL|Type of the certificate|CertificateType|DEVELOPER_ID_APPLICATION <br />DEVELOPER_ID_KEXT <br />IOS_DEVELOPMENT <br />IOS_DISTRIBUTION <br />MAC_APP_DEVELOPMENT <br />MAC_APP_DISTRIBUTION <br />MAC_INSTALLER_DISTRIBUTION|
|--display-name|DISPLAY_NAME|Code signing certificate display name|str||
|--certificate-key|PRIVATE_KEY|Private key used to generate the certificate. Used together with --save or --create options.|CertificateKeyArgument||
|--certificate-key-password|PRIVATE_KEY_PASSWORD|Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted.|CertificateKeyPasswordArgument||
|--p12-password|P12_CONTAINER_PASSWORD|If provided, the saved p12 container will be encrypted using this password. Used together with --save option.|str||
|--save|SAVE|Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.|bool||

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
