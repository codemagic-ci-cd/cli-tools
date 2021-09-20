from __future__ import annotations

import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
import time
from functools import reduce
from operator import add
from typing import IO
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from codemagic.cli import CliProcess
from codemagic.mixins import RunningCliAppMixin
from codemagic.utilities import log
from codemagic.utilities.backwards_file_reader import iter_backwards
from codemagic.utilities.levenshtein_distance import levenshtein_distance

from .export_options import ExportOptions
from .simulator import CoreSimulatorService
from .simulator import Simulator
from .xcpretty import Xcpretty


class Xcodebuild(RunningCliAppMixin):

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
            duration = time.strftime('%M:%S', time.gmtime(xcodebuild_cli_process.duration))
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

    def _construct_base_command(self, custom_flags: Optional[str]) -> List[str]:
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
        if custom_flags:
            command.extend([os.path.expandvars(part) for part in shlex.split(custom_flags)])
        return command

    def _construct_archive_command(self,
                                   archive_path: pathlib.Path,
                                   export_options: ExportOptions,
                                   xcargs: Optional[str],
                                   custom_flags: Optional[str]) -> List[str]:
        code_signing_options = []
        if not export_options.has_xcode_managed_profiles():
            if export_options.teamID:
                code_signing_options.append(f'DEVELOPMENT_TEAM={export_options.teamID}')
            if export_options.signingCertificate:
                code_signing_options.append(f'CODE_SIGN_IDENTITY={export_options.signingCertificate}')

        return [
            *self._construct_base_command(custom_flags),
            '-archivePath', str(archive_path),
            'archive',
            *shlex.split(xcargs or ''),
            *code_signing_options,
        ]

    def _construct_export_archive_command(self,
                                          archive_path: pathlib.Path,
                                          ipa_directory: pathlib.Path,
                                          export_options_plist: pathlib.Path,
                                          xcargs: Optional[str],
                                          custom_flags: Optional[str]) -> List[str]:
        return [
            'xcodebuild', '-exportArchive',
            '-archivePath', str(archive_path),
            '-exportPath', str(ipa_directory),
            '-exportOptionsPlist', str(export_options_plist),
            *[os.path.expandvars(part) for part in shlex.split(custom_flags or '')],
            *shlex.split(xcargs or ''),
        ]

    def _construct_test_command(self,
                                sdk: str,
                                simulators: List[Simulator],
                                only_testing: Optional[str],
                                enable_code_coverage: bool,
                                max_devices: Optional[int],
                                max_simulators: Optional[int],
                                xcargs: Optional[str],
                                custom_flags: Optional[str]) -> List[str]:
        max_devices_flag = '-maximum-concurrent-test-device-destinations'
        max_sims_flag = '-maximum-concurrent-test-simulator-destinations'

        destinations_args = [['-destination', f'id={s.udid}'] for s in simulators]
        only_testing_args = ['-only-testing', only_testing] if only_testing else []
        max_devices_args = [max_devices_flag, str(max_devices)] if max_devices else []
        max_simulators_args = [max_sims_flag, str(max_simulators)] if max_simulators else []
        coverage_args = ['-enableCodeCoverage', 'YES' if enable_code_coverage else 'NO']

        return [
            *self._construct_base_command(custom_flags),
            *only_testing_args,
            '-sdk', sdk,
            *coverage_args,
            *reduce(add, destinations_args, []),
            *max_devices_args,
            *max_simulators_args,
            'test',
            *shlex.split(xcargs or ''),
        ]

    def clean(self):
        cmd = [*self._construct_base_command(None), 'clean']
        self._run_command(cmd, f'Failed to clean {self.workspace or self.project}')

    def archive(self,
                export_options: ExportOptions,
                archive_directory: pathlib.Path,
                *,
                xcargs: Optional[str] = None,
                custom_flags: Optional[str] = None) -> pathlib.Path:
        CoreSimulatorService().ensure_clean_state()

        archive_directory.mkdir(parents=True, exist_ok=True)
        temp_dir = tempfile.mkdtemp(
            prefix=f'{self.xcode_project.stem}_',
            suffix='.xcarchive',
            dir=archive_directory,
        )
        xcarchive = pathlib.Path(temp_dir)

        cmd = self._construct_archive_command(xcarchive, export_options, xcargs, custom_flags)
        try:
            self._run_command(cmd, f'Failed to archive {self.workspace or self.project}')
        except IOError as error:
            if not self.xcpretty:
                raise
            message, process = error.args
            errors = _XcodebuildLogErrorFinder(self.logs_path).find_failure_logs()
            if not errors:
                raise
            raise IOError('\n'.join([f'{message}. The following build commands failed:', '', errors]), process)

        return xcarchive

    def export_archive(self,
                       archive_path: pathlib.Path,
                       export_options_plist: pathlib.Path,
                       ipa_directory: pathlib.Path,
                       *,
                       xcargs: Optional[str] = None,
                       custom_flags: Optional[str] = None) -> pathlib.Path:
        ipa_directory.mkdir(parents=True, exist_ok=True)

        cmd = self._construct_export_archive_command(
            archive_path, ipa_directory, export_options_plist, xcargs, custom_flags)
        self._run_command(cmd, f'Failed to export archive {archive_path}')

        try:
            return next(ipa_directory.glob('*.ipa'))
        except StopIteration:
            raise IOError(f'Ipa not found from {ipa_directory}')

    def test(self,
             sdk: str,
             simulators: List[Simulator],
             *,
             enable_code_coverage: bool = False,
             only_testing: Optional[str] = None,
             max_concurrent_devices: Optional[int] = None,
             max_concurrent_simulators: Optional[int] = None,
             xcargs: Optional[str] = None,
             custom_flags: Optional[str] = None):
        CoreSimulatorService().ensure_clean_state()
        cmd = self._construct_test_command(
            sdk, simulators, only_testing, enable_code_coverage,
            max_concurrent_devices, max_concurrent_simulators,
            xcargs, custom_flags)
        error_message = f'Failed to test {self.workspace or self.project}'
        self._run_command(cmd, error_message)

    def _run_command(self,
                     command: List[str],
                     error_message: str,
                     ignore_error_code: Optional[int] = None):
        process = None
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                process = XcodebuildCliProcess(command, xcpretty=self.xcpretty)
                cli_app.logger.info('Execute "%s"\n', process.safe_form)
                process.execute().raise_for_returncode(include_logs=False)
            else:
                subprocess.check_output(command)
        except subprocess.CalledProcessError as cpe:
            if ignore_error_code and ignore_error_code == cpe.returncode:
                return
            raise IOError(error_message, process)
        finally:
            self._log_process(process)


class XcodebuildCliProcess(CliProcess):

    def __init__(self, *args, xcpretty: Optional[Xcpretty] = None, **kwargs):
        super().__init__(*args, **kwargs)
        with tempfile.NamedTemporaryFile(prefix='xcodebuild_', suffix='.log', delete=False) as tf:
            self.log_path = pathlib.Path(tf.name)
        self._buffer: Optional[IO] = None
        self.xcpretty = xcpretty

    @property
    def stdout(self) -> str:
        return self.log_path.read_text()

    @property
    def stderr(self) -> str:
        return ''

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
            if self.xcpretty:
                self.xcpretty.flush()


class _XcodebuildLogErrorFinder:

    def __init__(self, log_path: Union[pathlib.Path, str]):
        self._log_path = pathlib.Path(log_path)
        self._backwards_log_iterator = iter_backwards(log_path)

    def _get_failed_commands(self):
        capture_lines = False
        error_lines = []
        for line in self._backwards_log_iterator:
            line = line.strip()
            if re.match(r'^\(\d+ failures?\)$', line):
                capture_lines = True
                continue
            elif line == 'The following build commands failed:':
                break
            elif capture_lines and line:
                error_lines.append(line)

        return error_lines

    def _get_failed_command_logs(self, failed_commands, max_lines) -> Dict[str, List[str]]:
        lines_cache: List[str] = []
        capture_lines = False
        logs: Dict[str, List[str]] = {}
        for line in self._backwards_log_iterator:
            line = line.strip()
            if not line:
                continue
            elif re.match(r'^\*\* [^ ]+ FAILED \*\*', line):  # Match lines like '** ARCHIVE FAILED **'
                # From here on upwards we can start looking for error logs
                capture_lines = True
                continue
            elif line in failed_commands:
                # Found a line that refers to a failed command, save its logs
                if line not in logs:
                    # Capture up to 10 last lines of the logs
                    log_lines = reversed(lines_cache[:max_lines])
                    logs[line] = ['...', *log_lines] if len(lines_cache) > max_lines else list(log_lines)
                if set(logs.keys()) == set(failed_commands):
                    # All errors are processed, stop
                    break
                lines_cache = []
            elif capture_lines:
                lines_cache.append(line)

        return logs

    @classmethod
    def _format_errors(cls, failed_command_logs: Dict[str, List[str]]) -> str:
        lines = []
        for error in sorted(failed_command_logs.keys()):
            lines.append(error)
            for log_line in failed_command_logs[error]:
                lines.append(f'\t{log_line}')
            lines.append('')
        return '\n'.join(lines[:-1])

    def find_failure_logs(self, max_lines_per_error=6) -> Optional[str]:
        failed_commands = self._get_failed_commands()
        failed_command_logs = self._get_failed_command_logs(failed_commands, max_lines_per_error)
        if not failed_command_logs:
            return None
        return self._format_errors(failed_command_logs)
