from __future__ import annotations

import json
import pathlib
import shlex
import shutil
import subprocess
from typing import Any
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from .byte_str_converter import BytesStrConverter
from .pbx_project import PbxProject

if TYPE_CHECKING:
    from codemagic_cli_tools.cli import CliApp


class BundleIdDetector(BytesStrConverter):

    def __init__(self, xcode_project: pathlib.Path):
        self.xcode_project = xcode_project.expanduser()

    @classmethod
    def _can_use_xcode(cls) -> bool:
        return shutil.which('xcodebuild') is not None

    def detect(self,
               target_name: Optional[str],
               configuration_name: Optional[str] = None,
               *, cli_app: Optional['CliApp'] = None) -> Counter[str]:
        """
        :raises: IOError, ValueError
        """
        bundle_ids = None
        if self._can_use_xcode():
            bundle_ids = self._detect_bundle_ids_with_xcode(target_name, configuration_name, cli_app)
        if not bundle_ids:
            bundle_ids = self._detect_bundle_ids_from_project(target_name, configuration_name, cli_app)
        return bundle_ids

    def _get_xcodebuild_command(self, target_name: Optional[str], configuration_name: Optional[str]) -> List[str]:
        cmd = ['xcodebuild', '-project', str(self.xcode_project)]
        if target_name is not None:
            cmd.extend(['-target', target_name])
        if configuration_name is not None:
            cmd.extend(['-configuration', configuration_name])
        cmd.extend(['-showBuildSettings', '-json'])
        return cmd

    def _detect_bundle_ids_with_xcode(self, target_name, configuration_name, cli_app) -> Counter[str]:
        cmd = self._get_xcodebuild_command(target_name, configuration_name)
        process = None
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
                stdout = process.stdout
            else:
                stdout = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()
        except subprocess.CalledProcessError as cpe:
            xcode_project = shlex.quote(str(self.xcode_project))
            error = f'Unable to detect Bundle ID from Xcode project {xcode_project}: {self._str(cpe.stderr)}'
            raise IOError(error, process)

        return Counter[str](
            build_setting['buildSettings']['PRODUCT_BUNDLE_IDENTIFIER']
            for build_setting in json.loads(stdout)
        )

    def _detect_bundle_ids_from_project(self, target_name, configuration_name, cli_app) -> Counter[str]:
        def get_targets(pbx_project: PbxProject):
            if target_name:
                return [pbx_project.get_target(target_name)]
            return pbx_project.get_targets()

        def get_configs(pbx_project: PbxProject, target: Dict[str, Any]):
            if configuration_name:
                return [pbx_project.get_target_config(target['name'], configuration_name)]
            return pbx_project.get_target_configs(target['name'])

        project = PbxProject.from_path(self.xcode_project / 'project.pbxproj', cli_app=cli_app)
        return Counter[str](
            project.get_bundle_id(target['name'], config['name'])
            for target in get_targets(project)
            for config in get_configs(project, target)
        )
