
create_certificate
==================
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``app-store-connect create-certificate [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--type {DEVELOPER_ID_APPLICATION, DEVELOPER_ID_KEXT, IOS_DEVELOPMENT, IOS_DISTRIBUTION, MAC_APP_DEVELOPMENT, MAC_APP_DISTRIBUTION, MAC_INSTALLER_DISTRIBUTION}] [--certificate-key PRIVATE_KEY] [--certificate-key-password PRIVATE_KEY_PASSWORD] [--p12-password P12_CONTAINER_PASSWORD] [--save] ``
#### Create code signing certificates of given type

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

### Optional arguments for command create_certificate

|Flags|Argument|Description|Type|Default|Choices|
| :--- | :--- | :--- | :--- | :--- | :--- |
|--type|CERTIFICATE_TYPE|Type of the certificate|CertificateType|IOS_DEVELOPMENT|DEVELOPER_ID_APPLICATION, DEVELOPER_ID_KEXT, IOS_DEVELOPMENT, IOS_DISTRIBUTION, MAC_APP_DEVELOPMENT, MAC_APP_DISTRIBUTION, MAC_INSTALLER_DISTRIBUTION|
|--certificate-key|PRIVATE_KEY|Private key used to generate the certificate. Used together with --save or --create options.|CertificateKeyArgument|||
|--certificate-key-password|PRIVATE_KEY_PASSWORD|Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted.|CertificateKeyPasswordArgument|||
|--p12-password|P12_CONTAINER_PASSWORD|If provided, the saved p12 container will be encrypted using this password. Used together with --save option.|str|||
|--save||Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.|bool|||

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
