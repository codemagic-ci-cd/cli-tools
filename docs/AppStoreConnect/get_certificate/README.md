
get_certificate
===============


``app-store-connect get-certificate [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}] [--certificate-key PRIVATE_KEY] [--certificate-key-password PRIVATE_KEY_PASSWORD] [--p12-password P12_CONTAINER_PASSWORD] [--save] CERTIFICATE_RESOURCE_ID``
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
|--certificate-key|PRIVATE_KEY|Private key used to generate the certificate. Used together with --save or --create options.|CertificateKeyArgument|
|--certificate-key-password|PRIVATE_KEY_PASSWORD|Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted.|CertificateKeyPasswordArgument|
|--p12-password|P12_CONTAINER_PASSWORD|If provided, the saved p12 container will be encrypted using this password. Used together with --save option.|str|
|--save||Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.|bool|

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
