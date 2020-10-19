from __future__ import annotations

import json
import pathlib
import re
import subprocess
from collections import Sequence
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .runtime import Runtime

if TYPE_CHECKING:
    from codemagic.cli import CliApp


@dataclass
class Simulator:
    udid: str
    is_available: bool
    state: str
    name: str
    data_path: pathlib.Path
    log_path: pathlib.Path

    def __post_init__(self):
        if isinstance(self.data_path, str):
            self.data_path = pathlib.Path(self.data_path)
        if isinstance(self.log_path, str):
            self.log_path = pathlib.Path(self.log_path)

    @classmethod
    def create(cls, **kwargs) -> Simulator:
        @lru_cache()
        def camel_to_snake(s: str) -> str:
            return re.sub(r'([A-Z])', lambda m: f'_{m.group(1).lower()}', s)

        return Simulator(**{
            camel_to_snake(name): value for name, value in kwargs.items()
            if camel_to_snake(name) in cls.__dataclass_fields__
        })

    def dict(self) -> Dict[str, Union[str, bool]]:
        return {**self.__dict__, 'data_path': str(self.data_path), 'log_path': str(self.log_path)}

    def __repr__(self):
        return f'<Simulator: {self.name!r}>'

    @classmethod
    def _list_devices(cls, cli_app: Optional[CliApp]) -> Dict[str, List[Dict]]:
        cmd_args = ('xcrun', 'simctl', 'list', 'devices', '--json')
        try:
            if cli_app:
                process = cli_app.execute(cmd_args, show_output=False)
                process.raise_for_returncode()
                stdout = process.stdout
            else:
                stdout = subprocess.check_output(cmd_args)
        except subprocess.CalledProcessError:
            raise IOError('Failed to list available test devices')
        return json.loads(stdout).get('devices', {})

    @classmethod
    def list(cls,
             runtimes: Optional[Sequence[Runtime]] = None,
             simulator_name: Optional[re.Pattern] = None,
             include_unavailable: bool = False,
             cli_app: Optional[CliApp] = None) -> Dict[Runtime, List[Simulator]]:
        runtime_simulators: Dict[Runtime, List[Simulator]] = {}
        for runtime_name, devices in cls._list_devices(cli_app).items():
            runtime = Runtime(runtime_name)
            if runtimes and runtime not in runtimes:
                continue  # Omit this runtime since it was not in the constraints

            simulators = (Simulator.create(**device) for device in devices)
            if not include_unavailable:
                simulators = (s for s in simulators if s.is_available)
            if simulator_name:
                simulators = (s for s in simulators if simulator_name.search(s.name))
            simulators = sorted(simulators, key=lambda s: s.name)

            if not simulators:
                continue  # Omit this runtime since it has no available devices
            runtime_simulators[runtime] = simulators

        return runtime_simulators
