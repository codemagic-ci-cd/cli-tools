
GitChangelog
============

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

### GitChangelog actions

|Action|Description|
| :--- | :--- |
|[generate](generate/README.md)|Generate a changelog text from git history|

### Optional arguments for GitChangelog

|Flags|Argument|Description|Type|Default|
| :--- | :--- | :--- | :--- | :--- |
|--previous-commit|PREVIOUS_COMMIT|Commit ID starting from which to generate the log|str||
|--skip-pattern|SKIP_PATTERN|Regex pattern to skip unneeded commit message lines|compile|^[Mm]erged? (remote-tracking )?(branch&#124;pull request&#124;in) .*|
|--commit-limit|COMMIT_LIMIT|Maxmimum number of commits to retrieve from git before filtering|int|50|
