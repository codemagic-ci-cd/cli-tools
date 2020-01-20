
delete_profile
==============

#### Delete specified Profile from Apple Developer portal.


``app-store-connect delete-profile [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--log-api-calls] [--json] [--issuer-id ISSUER_ID] [--key-id KEY_IDENTIFIER] [--private-key PRIVATE_KEY] [--certificates-dir CERTIFICATES_DIRECTORY] [--profiles-dir PROFILES_DIRECTORY] [--ignore-not-found] PROFILE_RESOURCE_ID``
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
### Required arguments for command delete_profile


**PROFILE_RESOURCE_ID**

Alphanumeric ID value of the Profile
### Optional arguments for command delete_profile


**--ignore-not-found**

Do not raise exceptions if the specified resource does not exist.
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