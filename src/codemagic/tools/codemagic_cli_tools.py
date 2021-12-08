import shutil
import sys
from distutils.version import LooseVersion

import requests

from codemagic import __version__
from codemagic import cli
from codemagic.cli import Colors


class CodemagicCliToolsError(cli.CliAppException):
    pass


class CodemagicCliTools(cli.CliApp):
    """
    Show general information of installed Codemagic CLI tools
    """

    @cli.action('version')
    def version(self, should_print: bool = True) -> str:
        """
        Show version of installed Codemagic CLI tools
        """
        if should_print:
            executable = self.get_executable_name()
            self.echo(f'{executable} {__version__}')
        return __version__

    @cli.action('installed-tools')
    def installed_tools(self):
        """
        Show installed Codemagic CLI tools
        """
        for tool_class in cli.CliApp.__subclasses__():
            executable = tool_class.get_executable_name()
            self.echo(f'{executable} installed at {shutil.which(executable) or executable}')

    @cli.action('upgrade')
    def upgrade(self):
        """
        Upgrade installed Codemagic CLI tools to latest available version
        """
        response = requests.get(
            'https://pypi.org/pypi/codemagic-cli-tools/json',
            headers={
                'Accept': 'application/json',
            },
        )

        if not response.ok:
            raise CodemagicCliToolsError('Checking most recent Codemagic CLI tools version failed')
        try:
            latest_version = response.json()['info']['version']
        except (ValueError, KeyError):
            raise CodemagicCliToolsError('Checking most recent Codemagic CLI tools version failed')

        current_version = self.version(should_print=False)
        if LooseVersion(latest_version) <= LooseVersion(current_version):
            self.echo(Colors.GREEN('Latest version %s is already installed'), latest_version)
            return

        self.echo(f'New version of Codemagic CLI tools is available ({latest_version} > {current_version})')
        self.echo(f'Install version {latest_version}')
        upgrade_command = [
            sys.executable, '-m', 'pip', 'install', '--upgrade', f'codemagic-cli-tools=={latest_version}',
        ]
        self.execute(upgrade_command, show_output=False)
        self.echo(Colors.GREEN(f'Successfully installed Codemagic CLI tools version {latest_version}'))


if __name__ == '__main__':
    CodemagicCliTools.invoke_cli()
