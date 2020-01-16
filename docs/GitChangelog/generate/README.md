
generate
========
<style> td { font-size: 85%; word-break: break-word; width: 16%;} table { width:100%; border-spacing: 1px;}</style>

``git-changelog generate [-h] [-s] [-v] [--no-color] [--log-stream {stderr, stdout}]  ``
#### Generate a changelog text from git history

### Optional arguments

|Flags|Description|
| :--- | :--- |
|-h, --help|show this help message and exit|

### Options

|Flags|Description|Choices|
| :--- | :--- | :--- |
|-s, --silent|Disable log output for commands||
|-v, --verbose|Enable verbose logging for commands||
|--no-color|Do not use ANSI colors to format terminal output||
|--log-stream|Log output stream. [Default: stderr]|stderr, stdout|

### Optional arguments for GitChangelog

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|<span style="white-space: nowrap">--previous-commit</span>|PREVIOUS_COMMIT|Commit ID starting from which to generate the log|str||
|<span style="white-space: nowrap">--skip-pattern</span>|SKIP_PATTERN|Regex pattern to skip unneeded commit message lines|compile|^[Mm]erged? (remote-tracking )?(branch&#124;pull request&#124;in) .*|
|<span style="white-space: nowrap">--commit-limit</span>|COMMIT_LIMIT|Maxmimum number of commits to retrieve from git before filtering|int|50|
