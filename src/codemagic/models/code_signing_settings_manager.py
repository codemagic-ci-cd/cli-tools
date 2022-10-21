from __future__ import annotations

import json
import pathlib
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic.cli import Colors
from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .certificate import Certificate
from .export_options import ExportOptions
from .export_options import ProvisioningProfileAssignment
from .provisioning_profile import ProvisioningProfile

if TYPE_CHECKING:
    from codemagic.cli import CliApp


@dataclass
class TargetInfo:
    build_configuration: str
    bundle_id: str
    project_name: str
    target_name: str
    provisioning_profile_uuid: Optional[str] = None

    @classmethod
    def sort_key(cls, target_info: TargetInfo) -> Tuple[str, str, str]:
        return (
            target_info.project_name,
            target_info.target_name,
            target_info.build_configuration,
        )


class CodeSigningSettingsManager(RunningCliAppMixin, StringConverterMixin):

    def __init__(self, profiles: List[ProvisioningProfile], keychain_certificates: List[Certificate]):
        self.profiles: Dict[str, ProvisioningProfile] = {profile.uuid: profile for profile in profiles}
        self._certificates = keychain_certificates
        self._target_infos: List[TargetInfo] = []
        self.logger = log.get_logger(self.__class__)

    @lru_cache()
    def _get_json_serialized_profiles(self) -> str:
        profiles = [self._serialize_profile(p) for p in self.profiles.values()]
        return json.dumps(profiles)

    def _serialize_profile(self, profile):
        usable_certificates = profile.get_usable_certificates(self._certificates)
        common_names = Counter[str](certificate.common_name for certificate in usable_certificates)
        most_popular_common = common_names.most_common(1)
        common_name = most_popular_common[0][0] if most_popular_common else ''
        return {
            'certificate_common_name': common_name,
            'name': profile.name,
            'team_id': profile.team_identifier,
            'team_name': profile.team_name,
            'bundle_id': profile.bundle_id,
            'specifier': profile.uuid,
            'xcode_managed': profile.xcode_managed,
            'certificates': [c.serial for c in profile.certificates],
        }

    @property
    def _code_signing_manager(self) -> str:
        executable = pathlib.Path(__file__) / '..' / '..' / 'scripts' / 'code_signing_manager.rb'
        return str(executable.resolve())

    @classmethod
    def _is_xcodeproj_gem_installed(cls, cli_app: Optional[CliApp]) -> bool:
        ruby = shutil.which('ruby')
        if ruby is None:
            return False

        cmd = (ruby, '-e', 'require "xcodeproj"')
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return False
        return True

    @classmethod
    def _format_build_config_meta(cls, build_config_info):
        profile = build_config_info['profile']
        project = build_config_info['project_name']
        target = build_config_info['target_name']
        config = build_config_info['build_configuration']
        return Colors.BLUE(
            f' - Using profile "{profile.name}" [{profile.uuid}] '
            f'for target "{target}" [{config}] from project "{project}"',
        )

    def _notify_target_profile_usage(self, targets_with_profile: Sequence[TargetInfo]):
        for target_info in targets_with_profile:
            if target_info.provisioning_profile_uuid is None:
                continue
            profile = self.profiles[target_info.provisioning_profile_uuid]
            message = (
                f' - Using profile "{profile.name}" [{profile.uuid}] '
                f'for target "{target_info.target_name}" [{target_info.build_configuration}] '
                f'from project "{target_info.project_name}"'
            )
            self.logger.info(Colors.BLUE(message))

    def _notify_target_missing_profiles(
            self,
            targets_with_profile: Sequence[TargetInfo],
            targets_without_profile: Sequence[TargetInfo],
    ):
        """
        Show warning only for targets that have the same bundle id prefix, configuration and project
        as some target for which provisioning profile was matched.
        For example, if target with bundle id "com.example.app" from project "ProjectName"
        with config "Debug" was assigned a profile. Then
        - target with bundle identifier "com.example.app.specifier" from "ProjectName" with
          config "Debug" would trigger a warning, since both project and configuration match with
          the target for which profile was assigned to, and bundle identifier inherits from the
          matched target identifier.
        - however target with bundle identifier "com.example.otherApp" from the same project
          would not trigger a warning as bundle id does not inherit from a target for which a
          was profile was assigned to.
        """

        for target_info in targets_without_profile:
            for matched_target_info in targets_with_profile:
                project_name_match = target_info.project_name == matched_target_info.project_name
                configuration_match = target_info.build_configuration == matched_target_info.build_configuration
                bundle_id_prefix_match = \
                    target_info.bundle_id == matched_target_info.bundle_id or \
                    target_info.bundle_id.startswith(f'{matched_target_info.bundle_id}.')

                if project_name_match and configuration_match and bundle_id_prefix_match:
                    message = (
                        f' - Did not find provisioning profile matching bundle identifier "{target_info.bundle_id}" '
                        f'for target "{target_info.target_name}" [{target_info.build_configuration}] '
                        f'from project "{target_info.project_name}"'
                    )
                    self.logger.info(Colors.YELLOW(message))
                    break

    def notify_profile_usage(self):
        self.logger.info(Colors.GREEN('Completed configuring code signing settings'))

        targets_with_profile = [ti for ti in self._target_infos if ti.provisioning_profile_uuid is not None]
        targets_without_profile = [ti for ti in self._target_infos if ti.provisioning_profile_uuid is None]

        if targets_with_profile:
            self._notify_target_profile_usage(targets_with_profile)
            self._notify_target_missing_profiles(targets_with_profile, targets_without_profile)
        else:
            message = 'Did not find matching provisioning profiles for code signing!'
            self.logger.warning(Colors.YELLOW(message))

    def _apply(self, xcode_project, result_file_name, verbose_logging: bool):
        cmd = [
            self._code_signing_manager,
            '--xcode-project', xcode_project,
            '--result-path', result_file_name,
            '--profiles', self._get_json_serialized_profiles(),
            '--verbose',
        ]

        process = None
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=verbose_logging or cli_app.verbose)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            xcode_project = shlex.quote(str(xcode_project))
            error_message = f'Failed to set code signing settings for {xcode_project}'
            if not self._is_xcodeproj_gem_installed(cli_app):
                error_message = '\n'.join([
                    error_message,
                    'Ruby gem "xcodeproj" is required to configure code signing settings',
                    f'Install it with {Colors.BOLD("[sudo] gem install xcodeproj")}',
                ])
            raise IOError(error_message, process)

    def use_profiles(self, xcode_project: pathlib.Path, verbose_logging: bool = False):
        with NamedTemporaryFile(mode='r', prefix='use_profiles_result_', suffix='.json') as results_file:
            self._apply(xcode_project, results_file.name, verbose_logging=verbose_logging)
            try:
                target_infos = json.load(results_file)
            except ValueError:
                target_infos = []

        self._target_infos.extend(TargetInfo(**target_info) for target_info in target_infos)
        self._target_infos.sort(key=TargetInfo.sort_key)

    def generate_export_options(self, custom_options: Optional[Dict]) -> ExportOptions:
        profile_assignments = [
            ProvisioningProfileAssignment(
                target_info.bundle_id,
                self.profiles[target_info.provisioning_profile_uuid],
            )
            for target_info in self._target_infos
            if target_info.provisioning_profile_uuid is not None
        ]
        export_options = ExportOptions.from_profile_assignments(profile_assignments)
        export_options.update(custom_options or {})
        return export_options
