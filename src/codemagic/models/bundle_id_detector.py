from __future__ import annotations

import json
import pathlib
import shlex
import shutil
import subprocess
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log

from .pbx_project import PbxProject


class BundleIdDetector(RunningCliAppMixin, StringConverterMixin):

    def __init__(self, xcode_project: pathlib.Path, target_name: Optional[str], config_name: Optional[str]):
        self.xcode_project = xcode_project.expanduser()
        self.target = target_name
        self.config = config_name
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def _can_use_xcodebuild(cls) -> bool:
        return shutil.which('xcodebuild') is not None

    def notify(self):
        prefix = f'Detect Bundle ID from {self.xcode_project}'
        if self.target and self.config:
            self.logger.info(f'{prefix} target {self.target!r} [{self.config!r}]')
        elif self.target:
            self.logger.info(f'{prefix} target {self.target!r}')
        elif self.config:
            self.logger.info(f'{prefix} build configuration {self.config!r}')
        else:
            self.logger.info(prefix)

    def detect(self) -> List[str]:
        """
        :raises: IOError, ValueError
        """
        bundle_ids = None
        if self._can_use_xcodebuild():
            bundle_ids = self._detect_with_xcodebuild()
        if not bundle_ids:
            bundle_ids = self._detect_from_project()
        return list(bundle_ids)

    def _get_xcodebuild_command(self) -> List[str]:
        cmd = ['xcodebuild', '-project', str(self.xcode_project)]
        if self.target is not None:
            cmd.extend(['-target', self.target])
        if self.config is not None:
            cmd.extend(['-configuration', self.config])
        cmd.extend(['-showBuildSettings', '-json'])
        return cmd

    def _detect_with_xcodebuild(self) -> Iterator[str]:
        cmd = self._get_xcodebuild_command()
        process = None
        cli_app = self.get_current_cli_app()
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

        return (
            build_setting['buildSettings']['PRODUCT_BUNDLE_IDENTIFIER']
            for build_setting in json.loads(stdout)
            if build_setting['buildSettings'].get('PRODUCT_BUNDLE_IDENTIFIER')
        )

    def _get_project_configs(self, pbx_project: PbxProject, target: Dict[str, Any]):
        if self.config:
            return [pbx_project.get_target_config(target['name'], self.config)]
        return pbx_project.get_target_configs(target['name'])

    def _get_project_targets(self, pbx_project: PbxProject):
        if self.target:
            return [pbx_project.get_target(self.target)]
        return pbx_project.get_targets()

    def _detect_from_project(self) -> Iterator[str]:
        project = PbxProject.from_path(self.xcode_project / 'project.pbxproj')
        return (
            project.get_bundle_id(target['name'], config['name'])
            for target in self._get_project_targets(project)
            for config in self._get_project_configs(project, target)
        )
