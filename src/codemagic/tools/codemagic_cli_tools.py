import shutil

from codemagic import __version__
from codemagic import cli


class CodemagicCliTools(cli.CliApp):
    """
    Show general information of installed Codemagic CLI tools
    """

    @cli.action('version')
    def version(self) -> str:
        """
        Show version of installed Codemagic CLI tools
        """
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


if __name__ == '__main__':
    CodemagicCliTools.invoke_cli()
