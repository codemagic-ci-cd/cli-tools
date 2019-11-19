#!/usr/bin/env python3

import collections
from typing import Optional, NoReturn

import cli


class GitChangelogError(cli.CliAppException):
    pass


class GitChangelogArgument(cli.Argument):
    PREVIOUS_COMMIT = cli.ArgumentValue(
        flags=('--previous-commit',),
        key='previous_commit',
        description='Commit ID starting from which to generate the log',
        is_action_kwarg=True,
        argparse_kwargs={'required': False, 'default': None},
    )


ChangelogEntry = collections.namedtuple(
    'ChangelogEntry', ('hash', 'date', 'author', 'description'), defaults=(None,) * 4)


class GitChangelog(cli.CliApp):
    """
    Generate a changelog text from git history
    """
    ENTRY_SEPARATOR = '\x1e'
    PARAM_SEPARATOR = '\x1f'
    # %H - full commit hash, %cd - commit date, %an - author name, %B - subject/description
    GIT_LOG_FORMAT = PARAM_SEPARATOR.join(('%H', '%cd', '%an', '%B')) + ENTRY_SEPARATOR
    CHANGELOG_LIMIT = 50

    @cli.action('generate', GitChangelogArgument.PREVIOUS_COMMIT)
    def generate(self, previous_commit: Optional[str] = None) -> NoReturn:
        """
        Generate a changelog text from git history
        """
        raw_log = self._get_raw_git_log()
        log_entries = self._get_changelog_list(raw_log, previous_commit)
        formatted_changelog = self._format_log(log_entries)
        print(formatted_changelog)

    def _get_raw_git_log(self):
        process = self.execute(
            ['git', 'log', f'--pretty=format:{self.GIT_LOG_FORMAT}', f'-n {self.CHANGELOG_LIMIT}'],
            show_output=False)
        if process.returncode != 0:
            raise GitChangelogError(process, 'Unable to execute git log')
        return process.stdout

    def _get_changelog_list(self, changelog, previous_commit):
        changelog_list = []
        changelog_entries = changelog.strip(f'\n{self.ENTRY_SEPARATOR}').split(f'{self.ENTRY_SEPARATOR}\n')
        for changelog_entry in changelog_entries:
            entry = ChangelogEntry(*changelog_entry.strip().split(self.PARAM_SEPARATOR))
            if previous_commit and entry.hash == previous_commit:
                break
            changelog_list.append(entry)
        return changelog_list

    @staticmethod
    def _format_log(entries):
        descriptions = [e.description for e in entries if e.description is not None]
        return '- ' + '\n- '.join(descriptions)


if __name__ == '__main__':
    GitChangelog.invoke_cli()
