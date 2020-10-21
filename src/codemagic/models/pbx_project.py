from __future__ import annotations

import pathlib
import plistlib
import shutil
import subprocess
import tempfile
from itertools import chain
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from codemagic.mixins import RunningCliAppMixin
from codemagic.mixins import StringConverterMixin
from codemagic.utilities import log


class PbxProject(RunningCliAppMixin, StringConverterMixin):

    def __init__(self, project_data: Dict[str, Any]):
        self.plist: Dict[str, Any] = project_data
        self._project = self._get_project_section()
        self.logger = log.get_logger(self.__class__)

    @classmethod
    def from_path(cls, path: pathlib.Path) -> PbxProject:
        """
        :param path: Path to project.pbxproj
        :raises: ValueError, IOError
        :return: PbxProject
        """
        if not path.exists():
            raise ValueError(f'Cannot initialize PBX Project from {path}, no such file.')
        elif not path.is_file():
            raise ValueError(f'Cannot initialize PBX Project from {path}, not a file.')

        try:
            parsed: Dict[str, Any] = plistlib.loads(path.read_bytes())
        except ValueError:
            xml = cls._convert_to_xml(path)
            parsed = plistlib.loads(xml)

        return PbxProject(parsed)

    @classmethod
    def _ensure_plutil(cls):
        if shutil.which('plutil') is None:
            raise IOError('Missing executable "plutil"')

    @classmethod
    def _convert_to_xml(cls, path: pathlib.Path) -> bytes:
        cls._ensure_plutil()
        with tempfile.NamedTemporaryFile(suffix='xml') as tf:
            cmd = ('plutil', '-convert', 'xml1', '-o', tf.name, str(path))
            cli_app = cls.get_current_cli_app()
            try:
                if cli_app:
                    process = cli_app.execute(cmd)
                    process.raise_for_returncode()
                else:
                    subprocess.check_output(cmd, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as cpe:
                reason = f'unable to read file: {cls._str(cpe.stderr)}'
                raise IOError(f'Cannot initialize PBX Project from {path}, {reason}')
            return pathlib.Path(tf.name).read_bytes()

    def _get_project_section(self) -> Dict[str, Any]:
        for key, value in self.plist.get('objects', {}).items():
            if not isinstance(value, dict):
                continue
            isa = value.get('isa')
            if isa and isa == 'PBXProject':
                return {'id': key, **value}
        raise ValueError('PBXProject section not found')

    def get_item(self, item_id: str) -> Dict[str, Any]:
        item = self.plist['objects'][item_id]
        return {'id': item_id, **item}

    def get_targets(self) -> List[Dict[str, Any]]:
        return [self.get_item(target_id) for target_id in self._project['targets']]

    def get_target(self, target_name: str) -> Dict[str, Any]:
        targets = self.get_targets()
        try:
            return next(target for target in targets if target['name'] == target_name)
        except StopIteration:
            target_names = ', '.join(repr(t['name']) for t in targets)
            raise ValueError(f'Project does not have target {target_name!r}. Available targets: {target_names}.')

    def get_target_configs(self, target_name: str) -> List[Dict[str, Any]]:
        target = self.get_target(target_name)
        return self._get_build_configurations(target['buildConfigurationList'])

    def get_target_config(self, target_name: str, config_name) -> Dict[str, Any]:
        configs = self.get_target_configs(target_name)
        try:
            return next(c for c in configs if c['name'] == config_name)
        except StopIteration:
            config_names = ', '.join(repr(c['name']) for c in configs)
            raise ValueError(
                f'Target {target_name!r} does not have build configuration {config_name!r}. '
                f'Available build configurations: {config_names}.')

    def _get_build_configurations(self, build_configurations_list_id: str) -> List[Dict[str, Any]]:
        build_conf_list = self.get_item(build_configurations_list_id)
        return [self.get_item(config_id) for config_id in build_conf_list['buildConfigurations']]

    def _resolve_variable(self, variable: str, target: Dict[str, Any], config_name: str) -> Optional[str]:
        """
        Looks for variable definition in target's buildConfiguration entries for the given configuration.
        If the variable is not found, looks for it in project's buildConfiguration entries.
        """
        build_configurations_list_ids = (target['buildConfigurationList'], self._project['buildConfigurationList'])
        all_build_configurations = map(self._get_build_configurations, build_configurations_list_ids)
        build_configurations = (config for config in chain(*all_build_configurations) if config['name'] == config_name)
        build_configuration: Dict[str, Any] = next(build_configurations, {})
        build_settings = build_configuration.get('buildSettings', {})
        try:
            value = build_settings[variable]
            self.logger.debug(f'Resolved {variable} for {target["name"]} [{config_name}]: {value}')
        except KeyError:
            self.logger.warning(
                f'Unable to resolve {variable} for {target["name"]} [{config_name}]: variable not found')
            value = None
        return value

    def get_bundle_id(self, target_name: str, config_name: str) -> str:
        target = self.get_target(target_name)
        bundle_id = self._resolve_variable('PRODUCT_BUNDLE_IDENTIFIER', target, config_name)
        if bundle_id is None:
            raise ValueError(f'Unable to obtain Bundle ID for target {target_name} [{config_name}]')
        return bundle_id
