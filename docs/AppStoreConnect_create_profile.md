
create_profile
==============


``app-store-connect create-profile [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls] [--json] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] [--type PROFILE_TYPE] [--name PROFILE_NAME] [--save] BUNDLE_ID_RESOURCE_ID --certificate-ids CERTIFICATE_RESOURCE_IDS --device-ids DEVICE_RESOURCE_IDS``
#### Create provisioning profile of given type

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
### Required arguments for command create_profile


**BUNDLE_ID_RESOURCE_ID**

Alphanumeric ID value of the Bundle ID. Type `ResourceId`

**--certificate-ids=CERTIFICATE_RESOURCE_IDS**

Alphanumeric ID value of the Signing Certificate. Type `ResourceId`. Multiple arguments

**--device-ids=DEVICE_RESOURCE_IDS**

Alphanumeric ID value of the Device. Type `ResourceId`. Multiple arguments
### Optional arguments for command create_profile


**--type={IOS_APP_ADHOC, IOS_APP_DEVELOPMENT, IOS_APP_INHOUSE, IOS_APP_STORE, MAC_APP_DEVELOPMENT, MAC_APP_DIRECT, MAC_APP_STORE, TVOS_APP_ADHOC, TVOS_APP_DEVELOPMENT, TVOS_APP_INHOUSE, TVOS_APP_STORE}**

Type of the provisioning profile. Type `ProfileType`. Default: `IOS_APP_DEVELOPMENT`

**--name=PROFILE_NAME**

Name of the provisioning profile. Type `str`

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