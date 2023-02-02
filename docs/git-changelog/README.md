
git-changelog
=============


**Generate a changelog text from git history**
### Usage
```bash
git-changelog [-h] [--log-stream STREAM] [--no-color] [--version] [-s] [-v]
    [--previous-commit PREVIOUS_COMMIT]
    [--skip-pattern SKIP_PATTERN]
    [--commit-limit COMMIT_LIMIT]
    ACTION
```
### Optional arguments for command `git-changelog`

##### `--previous-commit=PREVIOUS_COMMIT`


Commit ID starting from which to generate the log
##### `--skip-pattern=SKIP_PATTERN`


Regex pattern to skip unneeded commit message lines. Default:&nbsp;`^[Mm]erged? (remote-tracking )?(branch|pull request|in) .*`
##### `--commit-limit=COMMIT_LIMIT`


Maxmimum number of commits to retrieve from git before filtering. Default:&nbsp;`50`
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
|[`generate`](generate.md)|Generate a changelog text from git history|
