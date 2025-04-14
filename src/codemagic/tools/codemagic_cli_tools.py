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
        # Try to install with uv if possible as it is a lot faster than standard pip interface.
        if uv := shutil.which("uv"):
            command = (uv, "pip", "install", "--python", sys.executable, "androguard")
            uv_process = self.execute(command, show_output=False)
            if uv_process.returncode == 0:
                return
            # Installation with uv failed, try again with regular pip.

        # Just call ensurepip and ignore its returncode.
        # ensurepip module can be disabled on Linuxes when using system Python as pip is
        # managed by apt, deb etc. Exit code 1 doesn't necessarily mean that pip is not available.
        self.execute((sys.executable, "-m", "ensurepip"), show_output=False)

        try:
            pip_process = self.execute((sys.executable, "-m", "pip", "install", "androguard"), show_output=False)
            pip_process.raise_for_returncode()
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
