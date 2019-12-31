import pathlib
import shlex
import subprocess
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from .export_options import ExportOptions

if TYPE_CHECKING:
    from codemagic_cli_tools.cli import CliApp


class Xcodebuild:

    def __init__(self,
                 xcode_workspace: Optional[pathlib.Path] = None,
                 xcode_project: Optional[pathlib.Path] = None,
                 target_name: Optional[str] = None,
                 configuration_name: Optional[str] = None,
                 scheme_name: Optional[str] = None):
        self.workspace = xcode_workspace
        self.project = xcode_project
        self.scheme = scheme_name
        self.target = target_name
        self.configuration = configuration_name

    def _detect_scheme(self) -> str:
        raise NotImplemented

    def _construct_base_command(self) -> List[str]:
        cmd = ['xcodebuild']

        if self.workspace:
            cmd.extend(['-workspace', str(self.workspace)])
        elif self.project:
            cmd.extend(['-project', str(self.project)])
        else:
            raise ValueError('Missing project and workspace')

        if self.scheme:
            cmd.extend(['-scheme', self.scheme])
        elif self.target:
            cmd.extend(['-target', self.target])
        else:
            cmd.extend(['-scheme', self._detect_scheme()])

        if self.configuration:
            cmd.extend(['-config', self.configuration])

        return cmd

    def archive(self,
                archive_path: pathlib.Path,
                export_options: ExportOptions,
                use_xcpretty: bool = True,
                *,
                cli_app: Optional['CliApp'] = None):
        cmd = self._construct_base_command()
        cmd.extend(['-archivePath', str(archive_path)])
        cmd.append('archive')
        cmd.append('COMPILER_INDEX_STORE_ENABLE=NO')

        if not export_options.has_xcode_managed_profiles():
            cmd.append(f'DEVELOPMENT_TEAM={shlex.quote(export_options.teamID)}')
            cmd.append(f'CODE_SIGN_IDENTITY={shlex.quote(export_options.signingCertificate)}')

        if use_xcpretty:
            # TODO: Use Xcpretty if required
            pass

        process = None
        try:
            if cli_app:
                process = cli_app.execute(cmd)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise IOError(f'Failed to archive {self.workspace or self.project}', process)
        finally:
            # TODO: save Xcodebuild logs to file
            pass

    @classmethod
    def export_archive(cls,
                       archive_path: pathlib.Path,
                       ipa_path: pathlib.Path,
                       export_options_plist: pathlib.Path,
                       *,
                       cli_app: Optional['CliApp'] = None):
        cmd = (
            'xcodebuild',
            '-archivePath', archive_path,
            '-exportPath', ipa_path,
            '-exportOptionsPlist', export_options_plist,
            'COMPILER_INDEX_STORE_ENABLE=NO'
        )

        process = None
        try:
            if cli_app:
                process = cli_app.execute(cmd)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise IOError(f'Failed to export archive {archive_path}', process)
        finally:
            # TODO: save Xcodebuild logs to file
            pass