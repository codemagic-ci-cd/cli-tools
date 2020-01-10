#!/usr/bin/env python3

import re
import typing
from typing import Iterator
from typing import Optional
from typing import Pattern

from codemagic import cli


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
        type=re.compile,
        description='Regex pattern to skip unneeded commit message lines',
        argparse_kwargs={'required': False, 'default': '^[Mm]erged? (remote-tracking )?(branch|pull request|in) .*'},
    )

    COMMIT_LIMIT = cli.ArgumentProperties(
        flags=('--commit-limit',),
        key='commit_limit',
        type=int,
        description='Maxmimum number of commits to retrieve from git before filtering',
        argparse_kwargs={'required': False, 'default': 50},
    )


class ChangelogEntry(typing.NamedTuple):
    hash: str = ''
    date: str = ''
    author: str = ''
    description: str = ''


@cli.common_arguments(*GitChangelogArgument)
class GitChangelog(cli.CliApp):
    """
    Generate a changelog text from git history
    """
    ENTRY_SEPARATOR = '\x1e'
    PARAM_SEPARATOR = '\x1f'
    # %H - full commit hash, %cd - commit date, %an - author name, %B - subject/description
    GIT_LOG_FORMAT = PARAM_SEPARATOR.join(('%H', '%cd', '%an', '%B')) + ENTRY_SEPARATOR

    def __init__(self, *, previous_commit: Optional[str], skip_pattern: Pattern, commit_limit: int, **kwargs):
        super().__init__(**kwargs)
        self.previous_commit = previous_commit
        self.skip_pattern = skip_pattern
        self.commit_limit = commit_limit

    @cli.action('generate')
    def generate(self) -> Iterator[ChangelogEntry]:
        """
        Generate a changelog text from git history
        """
        raw_log = self._get_raw_git_log()
        log_entries = self._get_changelog_list(raw_log)
        formatted_changelog, changelog_line_count = self._format_log(log_entries)
        self.echo(formatted_changelog)
        self.logger.info(f'Generated {changelog_line_count} change log lines')
        return log_entries

    def _get_raw_git_log(self):
        process = self.execute(
            ['git', 'log', f'--pretty=format:{self.GIT_LOG_FORMAT}', f'-n {self.commit_limit}'],
            show_output=False)
        if process.returncode != 0:
            raise GitChangelogError('Unable to execute git log', process)
        raw_log = process.stdout.strip()
        if not raw_log:
            raise GitChangelogError('Aborting due to empty output from git log. Nothing to generate')
        return raw_log

    def _get_changelog_list(self, changelog) -> Iterator[ChangelogEntry]:
        changelog_entries = changelog.strip(f'\n{self.ENTRY_SEPARATOR}').split(f'{self.ENTRY_SEPARATOR}\n')
        previous_description = None
        for changelog_entry in changelog_entries:
            entry = ChangelogEntry(*changelog_entry.strip().split(self.PARAM_SEPARATOR))
            if self.previous_commit and entry.hash == self.previous_commit:
                break
            description = entry.description.strip()
            if description and description != previous_description:
                yield entry
            previous_description = description

    def _format_log(self, entries):
        descriptions = []
        for entry in entries:
            description_lines = [line for line in entry.description.split('\n') if self._should_include_log_line(line)]
            if description_lines:
                descriptions.append(f'* {description_lines[0]}')
                for line in description_lines[1:]:
                    descriptions.append(f'  {line}')
        formatted_log = '\n'.join(descriptions)
        return formatted_log, len(descriptions)

    def _should_include_log_line(self, line):
        return line.strip() and not self.skip_pattern.match(line.strip())


if __name__ == '__main__':
    GitChangelog.invoke_cli()
