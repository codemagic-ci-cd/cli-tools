
create_certificate
==================


``app-store-connect create-certificate [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls] [--json] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] [--type CERTIFICATE_TYPE] [--certificate-key PRIVATE_KEY] [--certificate-key-password PRIVATE_KEY_PASSWORD] [--p12-password P12_CONTAINER_PASSWORD] [--save] ``
#### Create code signing certificates of given type

### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream={stderr, stdout}**

Log output stream. [Default: stderr]
### Optional arguments for command create_certificate


**--type={DEVELOPER_ID_APPLICATION, DEVELOPER_ID_KEXT, IOS_DEVELOPMENT, IOS_DISTRIBUTION, MAC_APP_DEVELOPMENT, MAC_APP_DISTRIBUTION, MAC_INSTALLER_DISTRIBUTION}**

Type of the certificate. Type `CertificateType`. Default: `IOS_DEVELOPMENT`

**--certificate-key=PRIVATE_KEY**

Private key used to generate the certificate. Used together with --save or --create options. Type `CertificateKeyArgument`

**--certificate-key-password=PRIVATE_KEY_PASSWORD**

Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted. Type `CertificateKeyPasswordArgument`

**--p12-password=P12_CONTAINER_PASSWORD**

If provided, the saved p12 container will be encrypted using this password. Used together with --save option. Type `str`

**--save**

Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.
### Optional arguments for AppStoreConnect


**--log-api-calls**

Turn on logging for App Store Connect API HTTP requests

**--json**

Whether to show the resource in JSON format

**--issuer-id=ISSUER_ID**

App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. Type `IssuerIdArgument`

**--key-id=KEY_IDENTIFIER**

App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. Type `KeyIdentifierArgument`

**--private-key=PRIVATE_KEY**

App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. Type `PrivateKeyArgument`

**--certificates-dir=CERTIFICATES_DIRECTORY**

Directory where the code signing certificates will be saved. Type `Path`. Default: `$HOME/Library/MobileDevice/Certificates`

**--profiles-dir=PROFILES_DIRECTORY**

Directory where the provisioning profiles will be saved. Type `Path`. Default: `$HOME/Library/MobileDevice/Provisioning Profiles`