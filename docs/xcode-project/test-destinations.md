
test-destinations
=================


**List available destinations for test runs**
### Usage
```bash
xcode-project test-destinations [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-r RUNTIMES]
    [-n SIMULATOR_NAME]
    [-u]
    [--json]
```
### Optional arguments for action `test-destinations`

##### `-r, --runtime=RUNTIMES`


Runtime name. For example "iOS 14.1", "tvOS 14", "watchOS 7". Multiple arguments
##### `-n, --name=SIMULATOR_NAME`


Regex pattern to filter simulators by name. For example "iPad Air 2", "iPhone 11".
##### `-u, --include-unavailable`


Whether to include unavailable devices in output
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