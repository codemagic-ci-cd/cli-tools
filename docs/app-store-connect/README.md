
app-store-connect
=================


**Interact with Apple services via App Store Connect API**
### Usage
```bash
app-store-connect [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--log-api-calls]
    [--api-unauthorized-retries UNAUTHORIZED_REQUEST_RETRIES]
    [--api-server-error-retries SERVER_ERROR_RETRIES]
    [--disable-jwt-cache]
    [--json]
    [--issuer-id ISSUER_ID]
    [--key-id KEY_IDENTIFIER]
    [--private-key PRIVATE_KEY]
    [--certificates-dir CERTIFICATES_DIRECTORY]
    [--profiles-dir PROFILES_DIRECTORY]
    ACTION
```
### Optional arguments for command `app-store-connect`

##### `--log-api-calls`


Turn on logging for App Store Connect API HTTP requests
##### `--api-unauthorized-retries, -r=UNAUTHORIZED_REQUEST_RETRIES`


Specify how many times the App Store Connect API request should be retried in case the called request fails due to an authentication error (401 Unauthorized response from the server). In case of the above authentication error, the request is retried usinga new JSON Web Token as many times until the number of retries is exhausted. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_API_UNAUTHORIZED_RETRIES`. [Default: 3]
##### `--api-server-error-retries=SERVER_ERROR_RETRIES`


Specify how many times the App Store Connect API request should be retried in case the called request fails due to a server error (response with status code 5xx). In case of server error, the request is retried until the number of retries is exhausted. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_API_SERVER_ERROR_RETRIES`. [Default: 3]
##### `--disable-jwt-cache`


Turn off caching App Store Connect JSON Web Tokens to disk. By default generated tokens are cached to disk to be reused between separate processes, which can can reduce number of false positive authentication errors from App Store Connect API. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_DISABLE_JWT_CACHE`.
##### `--json`


Whether to show the resource in JSON format
##### `--issuer-id=ISSUER_ID`


App Store Connect API Key Issuer ID. Identifies the issuer who created the authentication token. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_ISSUER_ID`. Alternatively to entering `ISSUER_ID` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--key-id=KEY_IDENTIFIER`


App Store Connect API Key ID. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_KEY_IDENTIFIER`. Alternatively to entering `KEY_IDENTIFIER` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--private-key=PRIVATE_KEY`


App Store Connect API private key used for JWT authentication to communicate with Apple services. Learn more at https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api. If not provided, the key will be searched from the following directories in sequence for a private key file with the name `AuthKey_<key_identifier>.p8`: private_keys, ~/private_keys, ~/.private_keys, ~/.appstoreconnect/private_keys, where <key_identifier> is the value of `--key-id`. If not given, the value will be checked from the environment variable `APP_STORE_CONNECT_PRIVATE_KEY`. Alternatively to entering `PRIVATE_KEY` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `--certificates-dir=CERTIFICATES_DIRECTORY`


Directory where the code signing certificates will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Certificates`
##### `--profiles-dir=PROFILES_DIRECTORY`


Directory where the provisioning profiles will be saved. Default:&nbsp;`$HOME/Library/MobileDevice/Provisioning Profiles`
### Common options

##### `-h, --help`


show this help message and exit
##### `--log-stream=stderr | stdout`


Log output stream. Default `stderr`
##### `--no-color`


Do not use ANSI colors to format terminal output
##### `--version`


Show tool version and exit
##### `-s, --silent`


Disable log output for commands
##### `-v, --verbose`


Enable verbose logging for commands
### Actions

|Action|Description|
| :--- | :--- |
|[`create-bundle-id`](create-bundle-id.md)|Create Bundle ID in Apple Developer portal for specifier identifier|
|[`create-certificate`](create-certificate.md)|Create code signing certificates of given type|
|[`create-profile`](create-profile.md)|Create provisioning profile of given type|
|[`delete-bundle-id`](delete-bundle-id.md)|Delete specified Bundle ID from Apple Developer portal|
|[`delete-certificate`](delete-certificate.md)|Delete specified Signing Certificate from Apple Developer portal|
|[`delete-profile`](delete-profile.md)|Delete specified Profile from Apple Developer portal|
|[`fetch-signing-files`](fetch-signing-files.md)|Fetch provisioning profiles and code signing certificates         for Bundle ID with given identifier|
|[`get-bundle-id`](get-bundle-id.md)|Get specified Bundle ID from Apple Developer portal|
|[`get-certificate`](get-certificate.md)|Get specified Signing Certificate from Apple Developer portal|
|[`get-latest-app-store-build-number`](get-latest-app-store-build-number.md)|Get the latest App Store build number of the highest version for the given application|
|[`get-latest-build-number`](get-latest-build-number.md)|Get the highest build number of the highest version used for the given app.|
|[`get-latest-testflight-build-number`](get-latest-testflight-build-number.md)|Get the latest Testflight build number of the highest version for the given application|
|[`get-profile`](get-profile.md)|Get specified Profile from Apple Developer portal|
|[`list-builds`](list-builds.md)|List Builds from Apple Developer Portal matching given constraints|
|[`list-bundle-id-profiles`](list-bundle-id-profiles.md)|List provisioning profiles from Apple Developer Portal for specified Bundle IDs|
|[`list-bundle-ids`](list-bundle-ids.md)|List Bundle IDs from Apple Developer portal matching given constraints|
|[`list-certificates`](list-certificates.md)|List Signing Certificates from Apple Developer Portal matching given constraints|
|[`list-devices`](list-devices.md)|List Devices from Apple Developer portal matching given constraints|
|[`list-profiles`](list-profiles.md)|List Profiles from Apple Developer portal matching given constraints|
|[`publish`](publish.md)|Publish application packages to App Store, submit them to Testflight, and release to the groups of beta testers|
|[`register-device`](register-device.md)|Register a new device for app development|

### Action groups

|Action group|Description|
| :--- | :--- |
|[`app-store-version-localizations`](app-store-version-localizations.md)|Create and maintain version-specific App Store metadata that is localized.|
|[`app-store-version-submissions`](app-store-version-submissions.md)|Manage your application's App Store version review process|
|[`app-store-versions`](app-store-versions.md)|Manage the information related to an App Store version of your app|
|[`apps`](apps.md)|Manage your apps in App Store Connect|
|[`beta-app-review-submissions`](beta-app-review-submissions.md)|Manage your application's TestFlight submissions|
|[`beta-build-localizations`](beta-build-localizations.md)|Manage your beta builds localizations in App Store Connect|
|[`beta-groups`](beta-groups.md)|Manage your groups of beta testers in App Store Connect|
|[`builds`](builds.md)|Manage your builds in App Store Connect|
|[`review-submission-items`](review-submission-items.md)|Manage the contents of your review submission|
|[`review-submissions`](review-submissions.md)|Manage your App Store version review submissions|
