
pkg-info
========


**Show information about macOS Application Package file**
### Usage
```bash
xcode-project pkg-info [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--json]
    PKG_PATH
```
### Required arguments for action `pkg-info`

##### `PKG_PATH`


Path to MacOs Application Package file (.pkg)
### Optional arguments for action `pkg-info`

##### `--json`


Whether to show the resource in JSON format
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