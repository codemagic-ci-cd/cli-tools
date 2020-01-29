
detect‑bundle‑id
================


**Try to deduce the Bundle ID from specified Xcode project**
### Usage
```bash
xcode-project detect‑bundle‑id [-h] [-s] [-v] [--no-color] [--log-stream STREAM]
    [--project XCODE_PROJECT_PATTERN]
    [--target TARGET_NAME]
    [--config CONFIGURATION_NAME]
```
### Optional arguments for action `detect‑bundle‑id`

##### `--project=XCODE_PROJECT_PATTERN`


Path to Xcode project (\*.xcodeproj). Can be either a path literal, or a glob pattern to match projects in working directory. Multiple arguments. Default:&nbsp;`**/*.xcodeproj`
##### `--target=TARGET_NAME`


Name of the Xcode Target
##### `--config=CONFIGURATION_NAME`


Name of the Xcode build configuration
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