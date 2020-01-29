
list‑profiles
=============


**List Profiles from Apple Developer portal matching given constraints.**
### Usage
```bash
app-store-connect list‑profiles [-h] [-s] [-v] [--no-color] [--log-stream STREAM]
    [--log-api-calls]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    [--type PROFILE_TYPE_OPTIONAL]
    [--state PROFILE_STATE_OPTIONAL]
    [--name PROFILE_NAME]
    [--save]
```
### Optional arguments for action `list‑profiles`

##### `--type=IOS_APP_ADHOC | IOS_APP_DEVELOPMENT | IOS_APP_INHOUSE | IOS_APP_STORE | MAC_APP_DEVELOPMENT | MAC_APP_DIRECT | MAC_APP_STORE | TVOS_APP_ADHOC | TVOS_APP_DEVELOPMENT | TVOS_APP_INHOUSE | TVOS_APP_STORE`


Type of the provisioning profile
##### `--state=ACTIVE | INVALID`


State of the provisioning profile
##### `--name=PROFILE_NAME`


Name of the provisioning profile
##### `--save`


Whether to save the resources to disk. See PROFILES_DIRECTORY and CERTIFICATES_DIRECTORY for more information.
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--json`


Whether to show the resource in JSON format
##### `--issuer-id=ISSUER_ID`


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api.
##### `--certificates-dir=CERTIFICATES_DIRECTORY`


Directory where the code signing certificates will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates`
##### `--profiles-dir=PROFILES_DIRECTORY`


Directory where the provisioning profiles will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles`
### Common options

##### `-h, --help`


show this help message and exit
##### `-s, --silent`


Disable log output for commands
##### `-v, --verbose`


Enable verbose logging for commands
##### `--no-color`


Do not use ANSI colors to format terminal output
##### `--log-stream=stderr | stdout`


Log output stream. Default: stderr