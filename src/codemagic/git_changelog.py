#!/usr/bin/env python3

import argparse
import collections
import re
from typing import NoReturn, Optional, Pattern

from . import cli


class GitChangelogError(cli.CliAppException):
    pass


class GitChangelogArgument(cli.Argument):
    PREVIOUS_COMMIT = cli.ArgumentProperties(
        flags=('--previous-commit',),
        key='previous_commit',
        description='Commit ID starting from which to generate the log',
        argparse_kwargs={'required': False, 'default': None},
    )

    SKIP_PATTERN = cli.ArgumentProperties(
        flags=('--skip-pattern',),
        key='skip_pattern',
        description='Regex pattern to skip unneeded commit message lines',
        argparse_kwargs={'required': False, 'default': '^[Mm]erged? (remote-tracking )?(branch|pull request|in) .*'},
    )


ChangelogEntry = collections.namedtuple(
    'ChangelogEntry', ('hash', 'date', 'author', 'description'), defaults=(None,) * 4)


@cli.common_arguments(GitChangelogArgument.PREVIOUS_COMMIT, GitChangelogArgument.SKIP_PATTERN)
class GitChangelog(cli.CliApp):
    """
    Generate a changelog text from git history
    """
    ENTRY_SEPARATOR = '\x1e'
    PARAM_SEPARATOR = '\x1f'
    # %H - full commit hash, %cd - commit date, %an - author name, %B - subject/description
    GIT_LOG_FORMAT = PARAM_SEPARATOR.join(('%H', '%cd', '%an', '%B')) + ENTRY_SEPARATOR
    CHANGELOG_LIMIT = 50

    def __init__(self, previous_commit: Optional[str] = None, skip_pattern: Optional[Pattern] = None):
        super().__init__()
        self.previous_commit = previous_commit
        self.skip_pattern = skip_pattern

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        previous_commit = getattr(cli_args, GitChangelogArgument.PREVIOUS_COMMIT.value.key)
        pattern = getattr(cli_args, GitChangelogArgument.SKIP_PATTERN.value.key)
        return cls(previous_commit, re.compile(pattern))

    @cli.action('generate')
    def generate(self) -> NoReturn:
        """
        Generate a changelog text from git history
        """
        raw_log = self._get_raw_git_log()
        log_entries = self._get_changelog_list(raw_log)
        formatted_changelog = self._format_log(log_entries)
        print(formatted_changelog)

    def _get_raw_git_log(self):
        process = self.execute(
            ['git', 'log', f'--pretty=format:{self.GIT_LOG_FORMAT}', f'-n {self.CHANGELOG_LIMIT}'],
            show_output=False)
        if process.returncode != 0:
            raise GitChangelogError('Unable to execute git log', process)
        return process.stdout

    def _get_changelog_list(self, changelog):
        changelog_list = []
        changelog_entries = changelog.strip(f'\n{self.ENTRY_SEPARATOR}').split(f'{self.ENTRY_SEPARATOR}\n')
        for changelog_entry in changelog_entries:
            entry = ChangelogEntry(*changelog_entry.strip().split(self.PARAM_SEPARATOR))
            if self.previous_commit and entry.hash == self.previous_commit:
                break
            if not entry.description.strip():
                continue
            if changelog_list and entry.description == changelog_list[-1].description:
                continue
            changelog_list.append(entry)
        return changelog_list

    def _format_log(self, entries):
        descriptions = []
        for entry in entries:
            description_lines = [line for line in entry.description.split('\n') if self._should_include_log_line(line)]
            if description_lines:
                descriptions.append(f'* {description_lines[0]}')
                for line in description_lines[1:]:
                    descriptions.append(f'  {line}')
        return '\n'.join(descriptions)

    def _should_include_log_line(self, line):
        return line.strip() and not self.skip_pattern.match(line.strip())


if __name__ == '__main__':
    GitChangelog.invoke_cli()
