
fetch_signing_files
===================


**Fetch provisioning profiles and code signing certificates        for Bundle ID with given identifier.**
### Usage


``app-store-connect fetch-signing-files [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls] [--json] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] [--platform PLATFORM] [--certificate-key PRIVATE_KEY] [--certificate-key-password PRIVATE_KEY_PASSWORD] [--p12-password P12_CONTAINER_PASSWORD] [--type PROFILE_TYPE] [--create] BUNDLE_ID_IDENTIFIER``
### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream=stderr | stdout**

Log output stream. Default: stderr
### Required arguments for command fetch_signing_files


**BUNDLE_ID_IDENTIFIER**

Identifier of the Bundle ID
### Optional arguments for command fetch_signing_files


**--platform=IOS | MAC_OS**

Bundle ID platform. Default:&nbsp;`IOS`

**--certificate-key=PRIVATE_KEY**

Private key used to generate the certificate. Used together with --save or --create options.

**--certificate-key-password=PRIVATE_KEY_PASSWORD**

Password of the private key used to generate the certificate. Used together with --certificate-key or --certificate-key-path options if the provided key is encrypted.

**--p12-password=P12_CONTAINER_PASSWORD**

If provided, the saved p12 container will be encrypted using this password. Used together with --save option.

**--type=IOS_APP_ADHOC | IOS_APP_DEVELOPMENT | IOS_APP_INHOUSE | IOS_APP_STORE | MAC_APP_DEVELOPMENT | MAC_APP_DIRECT | MAC_APP_STORE | TVOS_APP_ADHOC | TVOS_APP_DEVELOPMENT | TVOS_APP_INHOUSE | TVOS_APP_STORE**

Type of the provisioning profile. Default:&nbsp;`IOS_APP_DEVELOPMENT`

**--create**

Whether to create the resource if it does not exist yet
### Optional arguments for app-store-connect


**--log-api-calls**

Turn on logging for App Store Connect API HTTP requests

**--json**

Whether to show the resource in JSON format

**--issuer-id=ISSUER_ID**

App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.

**--key-id=KEY_IDENTIFIER**

App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.

**--private-key=PRIVATE_KEY**

App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.

**--certificates-dir=CERTIFICATES_DIRECTORY**

Directory where the code signing certificates will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates`

**--profiles-dir=PROFILES_DIRECTORY**

Directory where the provisioning profiles will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles`