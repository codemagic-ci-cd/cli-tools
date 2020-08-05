from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import time
from typing import IO
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from codemagic.cli import CliProcess
from codemagic.utilities import log
from codemagic.utilities.levenshtein_distance import levenshtein_distance
from .export_options import ExportOptions
from .xcpretty import Xcpretty

if TYPE_CHECKING:
    from codemagic.cli import CliApp


class Xcodebuild:

    def __init__(self,
                 xcode_workspace: Optional[pathlib.Path] = None,
                 xcode_project: Optional[pathlib.Path] = None,
                 target_name: Optional[str] = None,
                 configuration_name: Optional[str] = None,
                 scheme_name: Optional[str] = None,
                 xcpretty: Optional[Xcpretty] = None):
        self.logger = log.get_logger(self.__class__)
        self.xcpretty = xcpretty
        self.workspace = xcode_workspace.expanduser() if xcode_workspace else None
        self.project = xcode_project.expanduser() if xcode_project else None
        self.scheme = scheme_name
        self.target = target_name
        self.configuration = configuration_name
        self._ensure_scheme_or_target()
        self.logs_path = self._get_logs_path()

    def _get_logs_path(self) -> pathlib.Path:
        tmp_dir = pathlib.Path('/tmp')
        if not tmp_dir.is_dir():
            tmp_dir = pathlib.Path(tempfile.gettempdir())
        logs_dir = tmp_dir / 'xcodebuild_logs'
        logs_dir.mkdir(exist_ok=True)
        prefix = f'{self.xcode_project.stem}_'
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix='.log', dir=logs_dir) as tf:
            return pathlib.Path(tf.name)

    def _log_process(self, xcodebuild_cli_process: Optional[XcodebuildCliProcess]):
        if not xcodebuild_cli_process:
            return
        with self.logs_path.open('a') as fd, xcodebuild_cli_process.log_path.open('r') as process_logs:
            fd.write(f'>>> {xcodebuild_cli_process.safe_form}')
            fd.write('\n\n')

            chunk = process_logs.read(8192)
            while chunk:
                fd.write(chunk)
                chunk = process_logs.read(8192)
            # do an extra read in case xcodebuild exited unexpectedly and did not flush last buffer
            fd.write(process_logs.read()) 

            fd.write('\n\n')
            duration = time.strftime("%M:%S", time.gmtime(xcodebuild_cli_process.duration))
            fd.write(f'<<< Process completed with status code {xcodebuild_cli_process.returncode} in {duration}')
            fd.write('\n\n')

    @property
    def xcode_project(self):
        if self.workspace and not self.project:
            return self.workspace.parent / f'{self.workspace.stem}.xcodeproj'
        elif self.project:
            return self.project
        else:
            raise ValueError('Missing project and workspace')

    def _ensure_scheme_or_target(self):
        project = self.xcode_project
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
                export_options: ExportOptions,
                archive_directory: pathlib.Path,
                *,
                cli_app: Optional['CliApp'] = None) -> pathlib.Path:
        archive_directory.mkdir(parents=True, exist_ok=True)
        temp_dir = tempfile.mkdtemp(
            prefix=f'{self.xcode_project.stem}_',
            suffix='.xcarchive',
            dir=archive_directory,
        )
        xcarchive = pathlib.Path(temp_dir)
        cmd = self._construct_archive_command(xcarchive, export_options)

        process = None
        try:
            if cli_app:
                process = XcodebuildCliProcess(cmd, xcpretty=self.xcpretty)
                cli_app.logger.info(f'Execute "%s"\n', process.safe_form)
                process.execute().raise_for_returncode()
            else:
                subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise IOError(f'Failed to archive {self.workspace or self.project}', process)
        finally:
            self._log_process(process)
        return xcarchive

    def export_archive(self,
                       archive_path: pathlib.Path,
                       export_options_plist: pathlib.Path,
                       ipa_directory: pathlib.Path,
                       *,
                       cli_app: Optional['CliApp'] = None) -> pathlib.Path:
        ipa_directory.mkdir(parents=True, exist_ok=True)
        cmd = (
            'xcodebuild', '-exportArchive',
            '-archivePath', archive_path,
            '-exportPath', ipa_directory,
            '-exportOptionsPlist', export_options_plist,
            'COMPILER_INDEX_STORE_ENABLE=NO'
        )

        process = None
        try:
            if cli_app:
                process = XcodebuildCliProcess(cmd, xcpretty=self.xcpretty)
                cli_app.logger.info(f'Execute "%s"\n', process.safe_form)
                process.execute().raise_for_returncode()
            else:
                subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise IOError(f'Failed to export archive {archive_path}', process)
        finally:
            self._log_process(process)

        try:
            return next(ipa_directory.glob('*.ipa'))
        except StopIteration:
            raise IOError(f'Ipa not found from {ipa_directory}')


class XcodebuildCliProcess(CliProcess):

    def __init__(self, *args, xcpretty: Optional[Xcpretty] = None, **kwargs):
        super().__init__(*args, **kwargs)
        with tempfile.NamedTemporaryFile(prefix='xcodebuild_', suffix='.log', delete=False) as tf:
            self.log_path = pathlib.Path(tf.name)
        self._buffer: Optional[IO] = None
        self.xcpretty = xcpretty

    def _print_stream(self, chunk: str):
        if not self._print_streams:
            return
        elif self.xcpretty:
            self.xcpretty.format(chunk)
        else:
            sys.stdout.write(chunk)

    def _handle_streams(self, buffer_size: Optional[int] = None):
        if not self._buffer:
            self._buffer = self.log_path.open('r')
        lines = self._buffer.readlines(buffer_size or -1)
        chunk = ''.join(lines)
        self._print_stream(chunk)
        self.stdout += chunk

    def execute(self, *args, **kwargs) -> XcodebuildCliProcess:
        try:
            with self.log_path.open('wb') as log_fd:
                kwargs.update({'stdout': log_fd, 'stderr': log_fd})
                super(XcodebuildCliProcess, self).execute(*args, **kwargs)
                return self
        finally:
            if self._buffer:
                self._buffer.close()
                self._buffer = None
