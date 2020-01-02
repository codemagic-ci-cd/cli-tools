from __future__ import annotations

import io
import logging
import pathlib
import subprocess
import sys
import threading
import time
from typing import IO
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from codemagic_cli_tools.cli import CliProcess
from codemagic_cli_tools.utilities.levenshtein_distance import levenshtein_distance
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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.workspace = xcode_workspace.expanduser() if xcode_workspace else None
        self.project = xcode_project.expanduser() if xcode_project else None
        self.scheme = scheme_name
        self.target = target_name
        self.configuration = configuration_name
        self._ensure_scheme_or_target()

    def _ensure_scheme_or_target(self):
        if self.workspace and not self.project:
            project = self.workspace.parent / f'{self.workspace.stem}.xcodeproj'
        elif self.project:
            project = self.project
        else:
            raise ValueError('Missing project and workspace')

        if self.target or self.scheme:
            return

        schemes = self._detect_schemes(project)
        if not schemes:
            raise ValueError(f'Did not find any schemes for {project}. Please specify scheme or target manually')
        self.logger.debug(f'Found schemes {", ".join(map(repr, schemes))}')
        self.scheme = self._find_matching_scheme(schemes, project.stem)
        self.logger.debug(f'Using scheme {self.scheme!r}')

    @classmethod
    def _find_matching_scheme(cls, schemes: List[str], reference_name: str) -> str:
        return min(schemes, key=lambda scheme: levenshtein_distance(reference_name, scheme))

    @classmethod
    def _detect_schemes(cls, project: pathlib.Path) -> List[str]:
        return [scheme.stem for scheme in project.glob('**/*.xcscheme')]

    def _construct_archive_command(self, archive_path: pathlib.Path, export_options: ExportOptions) -> List[str]:
        command = ['xcodebuild']

        if self.workspace:
            command.extend(['-workspace', str(self.workspace)])
        if self.project:
            command.extend(['-project', str(self.project)])
        if self.scheme:
            command.extend(['-scheme', self.scheme])
        if self.target:
            command.extend(['-target', self.target])
        if self.configuration:
            command.extend(['-config', self.configuration])

        command.extend([
            '-archivePath', str(archive_path),
            'archive',
            'COMPILER_INDEX_STORE_ENABLE=NO'
        ])

        if not export_options.has_xcode_managed_profiles():
            if export_options.teamID:
                command.append(f'DEVELOPMENT_TEAM={export_options.teamID}')
            if export_options.signingCertificate:
                command.append(f'CODE_SIGN_IDENTITY={export_options.signingCertificate}')

        return command

    def archive(self,
                archive_path: pathlib.Path,
                export_options: ExportOptions,
                use_xcpretty: bool = True,
                *,
                cli_app: Optional['CliApp'] = None):
        cmd = self._construct_archive_command(archive_path, export_options)

        if use_xcpretty:
            # TODO: Use Xcpretty if required
            pass

        process = None
        try:
            if cli_app:
                process = XcodebuildCliProcess(cmd, use_xcpretty=use_xcpretty).execute()
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise IOError(f'Failed to archive {self.workspace or self.project}', process)
        finally:
            pass

    @classmethod
    def export_archive(cls,
                       archive_path: pathlib.Path,
                       ipa_path: pathlib.Path,
                       export_options_plist: pathlib.Path,
                       *,
                       cli_app: Optional['CliApp'] = None):
        cmd = (
            'xcodebuild', '-exportArchive',
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


class XcodebuildCliProcess(CliProcess):

    def __init__(self, *args, use_xcpretty: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_path = pathlib.Path('/tmp/xcodebuild.log')
        self._log_offset: int = 0
        self.use_xcpretty = use_xcpretty

    def _handle_streams(self, buffer_size: Optional[int] = None):
        with self._log_path.open('rb') as fd:
            fd.seek(self._log_offset)
            read_bytes = fd.read(buffer_size) if buffer_size else fd.read()

        self._log_offset += len(read_bytes)
        chunk = read_bytes.decode()

        if self._print_streams:
            if not self.use_xcpretty:
                sys.stdout.write(chunk)
            else:
                xcpretty = subprocess.Popen(['xcpretty'], stdin=subprocess.PIPE)
                xcpretty.communicate(input=read_bytes, timeout=5)

        self.stdout += chunk

    def execute(self, *args, **kwargs) -> CliProcess:
        with self._log_path.open('wb') as log_fd:
            kwargs.update({'stdout': log_fd, 'stderr': log_fd})
            return super(XcodebuildCliProcess, self).execute(*args, **kwargs)
