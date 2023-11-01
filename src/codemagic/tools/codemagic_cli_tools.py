import pathlib
import shutil
import textwrap

import argcomplete

from codemagic import __version__
from codemagic import cli
from codemagic.cli import Colors


class CodemagicCliTools(cli.CliApp):
    """
    Show general information of installed Codemagic CLI tools
    """

    @cli.action("version")
    def version(self) -> str:
        """
        Show version of installed Codemagic CLI tools
        """
        executable = self.get_executable_name()
        self.echo(f"{executable} {__version__}")
        return __version__

    @cli.action("installed-tools")
    def installed_tools(self):
        """
        Show installed Codemagic CLI tools
        """
        for tool_class in cli.CliApp.__subclasses__():
            executable = tool_class.get_executable_name()
            self.echo(f"{executable} installed at {shutil.which(executable) or executable}")

    @cli.action("enable-shell-autocompletion")
    def enable_shell_autocompletion(self):
        """
        Enable tab autocompletion for Codemagic CLI tools in your shell
        """

        executables = [tool_class.get_executable_name() for tool_class in cli.CliApp.__subclasses__()]

        completion_scripts_dir = pathlib.Path("~/.codemagic-cli-tools/completions").expanduser()
        completion_scripts_dir.mkdir(parents=True, exist_ok=True)

        zsh_completion_path = completion_scripts_dir / "zsh_autocomplete.sh"
        zsh_completion_path.write_text(argcomplete.shellcode(executables, shell="zsh"))

        bash_completion_path = completion_scripts_dir / "bash_autocomplete.sh"
        bash_completion_path.write_text(argcomplete.shellcode(executables, shell="bash"))

        completion_path = completion_scripts_dir / "autocomplete.sh"
        completion_path.write_text(
            textwrap.dedent(
                f"""\
                #!/bin/sh

                if [ -n "$BASH_VERSION" ]; then
                  source {bash_completion_path}
                elif [ -n "$ZSH_VERSION" ]; then
                  source {zsh_completion_path}
                fi

                """,
            ),
        )

        self.echo(Colors.GREEN(f"Shell autocompletion instructions were saved to {completion_path}"))
        self.echo(
            "To use autocomplete for Codemagic CLI tools, add the following "
            "line to your shell profile (~/.zshrc, ~/.bashrc, etc):",
        )
        self.echo("")
        self.echo(Colors.WHITE(f"  source {completion_path}"))
        self.echo("")
        self.echo("Don't forget to source the completion script in your current shell.")


if __name__ == "__main__":
    CodemagicCliTools.invoke_cli()
