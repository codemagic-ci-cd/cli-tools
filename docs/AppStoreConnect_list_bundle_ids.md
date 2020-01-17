
list_bundle_ids
===============


``app-store-connect list-bundle-ids [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls] [--json] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] [--bundle-id-identifier BUNDLE_ID_IDENTIFIER_OPTIONAL] [--name BUNDLE_ID_NAME] [--platform PLATFORM_OPTIONAL] ``
#### List Bundle IDs from Apple Developer portal matching given constraints.

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
### Optional arguments for command list_bundle_ids


**--bundle-id-identifier=BUNDLE_ID_IDENTIFIER_OPTIONAL**

Identifier of the Bundle ID. Type `str`

**--name=BUNDLE_ID_NAME**

Name of the Bundle ID. If the resource is being created, the default will be deduced from given Bundle ID identifier. Type `str`

**--platform={IOS, MAC_OS}**

Bundle ID platform. Type `BundleIdPlatform`
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