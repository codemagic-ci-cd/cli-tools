
xcode-project
=============


**Utility to prepare iOS application code signing properties for build**
### Usage
```bash
xcode-project [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    ACTION
```
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
|[<nobr><code>build-ipa</code></nobr>](build-ipa.md)|Build ipa by archiving the Xcode project and then exporting it|
|[<nobr><code>detect-bundle-id</code></nobr>](detect-bundle-id.md)|Try to deduce the Bundle ID from specified Xcode project|
|[<nobr><code>use-profiles</code></nobr>](use-profiles.md)|Set up code signing settings on specified Xcode projects         to use given provisioning profiles|
