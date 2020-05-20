
android-app-bundle
==================


**Manage Android App Bundles using     [Bundletool](https://developer.android.com/studio/command-line/bundletool)**
### Usage
```bash
android-app-bundle [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
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
|[`build‑apks`](build-apks.md)|Generates an APK Set archive containing either all possible split APKs and         standalone APKs or APKs optimized for the connected device (see connected-         device flag). Returns list of generated APK set archives.|
|[`build‑universal‑apk`](build-universal-apk.md)|Shortcut for `build-apks` to build universal APKs from bundles.|
|[`dump`](dump.md)|Get files list or extract values from the bundle in a human-readable form.|
|[`validate`](validate.md)|Verify that given Android App Bundle is valid and print         out information about it.|
|[`version`](version.md)|Get Bundletool version|
