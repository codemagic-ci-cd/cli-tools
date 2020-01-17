
generate
========


``git-changelog generate [-h] [-s] [-v] [--no-color] [--log-stream CHOSEN_OPTION] [--previous-commit PREVIOUS_COMMIT] [--skip-pattern SKIP_PATTERN] [--commit-limit COMMIT_LIMIT]  ``
#### Generate a changelog text from git history

### Optional arguments


**-h, --help**

show this help message and exit

**-s, --silent**

Disable log output for commands

**-v, --verbose**

Enable verbose logging for commands

**--no-color**

Do not use ANSI colors to format terminal output

**--log-stream={stderr, stdout}**

Log output stream. [Default: stderr]
### Optional arguments for GitChangelog


**--previous-commit=PREVIOUS_COMMIT**

Commit ID starting from which to generate the log. Type `str`. Default: `None`

**--skip-pattern=SKIP_PATTERN**

Regex pattern to skip unneeded commit message lines. Type `compile`. Default: `^[Mm]erged? (remote-tracking )?(branch|pull request|in) .*`

**--commit-limit=COMMIT_LIMIT**

Maxmimum number of commits to retrieve from git before filtering. Type `int`. Default: `50`