import importlib.util
import shutil
import subprocess
import sys

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

    def _install_androguard(self):
        # Ignore ensurepip failures. For example ensurepip is disabled in Debian/Ubuntu for the system python
        # and it exits with error. This doesn't mean that pip isn't available.
        self.execute([sys.executable, "-m", "ensurepip"], show_output=False)
        try:
            cli_process = self.execute([sys.executable, "-m", "pip", "install", "androguard"], show_output=False)
            cli_process.raise_for_returncode()
        except subprocess.CalledProcessError:
            self.logger.error(Colors.RED("ERROR: Installing Androguard failed."))
            raise

    @cli.action(
        "ensure-androguard",
        suppress_help=True,
    )
    def ensure_androguard(self, notify_installed: bool = True) -> None:
        """
        Make sure that Codemagic CLI tools environment has Androguard dependency which
        is required to work with Android APK files. Whenever Androguard is missing but
        required by some action it will be installed automatically if need be.
        """
        if importlib.util.find_spec("androguard"):
            if notify_installed:
                self.logger.info(Colors.GREEN("Androguard is already installed"))
            return  # Androguard is already present, no need to install anything

        self.logger.info(Colors.WHITE("Installing Androguard to work with APK files..."))
        try:
            self._install_androguard()
        except subprocess.CalledProcessError as cpe:
            raise cli.CliAppException("Installing Androguard failed") from cpe
        self.logger.info(Colors.GREEN("Androguard successfully installed"))


if __name__ == "__main__":
    CodemagicCliTools.invoke_cli()
