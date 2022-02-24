
create
======


**Create an Android keystore**
### Usage
```bash
android-keystore create [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-l KEY_PASSWORD]
    [-o]
    [--validity VALIDITY_DAYS]
    -k KEYSTORE_PATH
    -p KEYSTORE_PASSWORD
    -a KEY_ALIAS
    [-CN COMMON_NAME]
    [-O ORGANIZATION]
    [-OU ORGANIZATION_UNIT]
    [-L LOCALITY]
    [-ST STATE_OR_PROVINCE]
    [-C COUNTRY]
    [-DN DISTINGUISHED_NAME]
```
### Required arguments for action `create`

##### `-k, --ks, --keystore=KEYSTORE_PATH`


Path where your keystore should be created or read from
##### `-p, --ks-pass, --keystore-pass=KEYSTORE_PASSWORD`


Secure password for your keystore. If not given, the value will be checked from the environment variable `ANDROID_KEYSTORE_PASSWORD`. Alternatively to entering `KEYSTORE_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`.
##### `-a, --ks-key-alias, --alias=KEY_ALIAS`


An identifying name for your keystore key
### Optional arguments for action `create`

##### `-l, --ks-key-pass, --key-pass=KEY_PASSWORD`


Secure password for your keystore key. Keystore password specified by `--keystore-pass` will be used in case it is not given. If not given, the value will be checked from the environment variable `ANDROID_KEYSTORE_KEY_PASSWORD`. Alternatively to entering `KEY_PASSWORD` in plaintext, it may also be specified using the `@env:` prefix followed by an environment variable name, or the `@file:` prefix followed by a path to the file containing the value. Example: `@env:<variable>` uses the value in the environment variable named `<variable>`, and `@file:<file_path>` uses the value from the file at `<file_path>`. [Default: None]
##### `-o, --overwrite-existing`


Overwrite keystore at specified path in case it exists
##### `--validity=VALIDITY_DAYS`


How long will the keystore be valid in days. Default:&nbsp;`10000`
### Optional arguments to set keystore issuer information. At least one is required

##### `-CN, --common-name=COMMON_NAME`


Common name of the keystore issuer. Either first and last name or company name
##### `-O, --organization=ORGANIZATION`


Organization of the keystore issuer
##### `-OU, --organization-unit=ORGANIZATION_UNIT`


Organizational unit of the keystore issuer. For example `engineering`
##### `-L, --locality=LOCALITY`


Identifies the place where the keystore issuer resides. Locality can be a city, county, township, or other geographic region
##### `-ST, --state=STATE_OR_PROVINCE`


Identifies the state or province in which the keystore issuer resides
##### `-C, --country=COUNTRY`


Two-letter code of the country in which the keystore issuer resides
##### `-DN, --distinguished-name=DISTINGUISHED_NAME`


Instead of individually defining all keystore issuer attributes, it is possible to just define the distinguished name or the certificate that is included in the keystore. It should describe you or your company as the certificate issuer. If defined it takes precedence over individually set attributes. For example `CN=corp.example.com,L=Mountain View,C=US`
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