
test-summary
============


**Show summary of Xcode Test Result**
### Usage
```bash
xcode-project test-summary [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [-p XCRESULT_PATTERNS]
    [-d XCRESULT_DIRS]
```
### Optional arguments for action `test-summary`

##### `-p, --xcresult=XCRESULT_PATTERNS`


Path to Xcode Test result (\*.xcresult) to be be converted. Can be either a path literal, or a glob pattern to match xcresults in working directory. If no search paths are provided, look for \*.xcresults from current directory. Multiple arguments
##### `-d, --dir=XCRESULT_DIRS`


Directory where Xcode Test results (\*.xcresult) should be converted. If no search paths are provided, look for \*.xcresults from current directory. Multiple arguments
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
