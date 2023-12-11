from __future__ import annotations

import json
import pathlib
import re
import subprocess
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.mixins import RunningCliAppMixin
from codemagic.utilities import case_conversion

from .runtime import Runtime


@dataclass
class Simulator(RunningCliAppMixin):
    udid: str
    is_available: bool
    state: str
    name: str
    data_path: pathlib.Path
    log_path: pathlib.Path
    runtime: Runtime

    def __post_init__(self):
        if isinstance(self.data_path, str):
            self.data_path = pathlib.Path(self.data_path)
        if isinstance(self.log_path, str):
            self.log_path = pathlib.Path(self.log_path)

    def __repr__(self):
        return f"<Simulator: {self.name!r}>"

    def dict(self) -> Dict[str, Union[str, bool]]:
        return {
            **self.__dict__,
            "data_path": str(self.data_path),
            "log_path": str(self.log_path),
            "runtime": str(self.runtime),
        }

    @classmethod
    def create(cls, **kwargs) -> Simulator:
        return Simulator(
            **{
                case_conversion.camel_to_snake(name): value
                for name, value in kwargs.items()
                if case_conversion.camel_to_snake(name) in cls.__dataclass_fields__  # type: ignore
            },
        )

    @classmethod
    def _list_devices(cls) -> Dict[str, List[Dict]]:
        cmd_args = ("xcrun", "simctl", "list", "devices", "--json")
        stdout: Union[bytes, str]
        cli_app = cls.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd_args, suppress_output=True)
                process.raise_for_returncode()
                stdout = process.stdout
            else:
                stdout = subprocess.check_output(cmd_args)
        except subprocess.CalledProcessError:
            raise IOError("Failed to list available test devices")
        return json.loads(stdout).get("devices", {})

    @classmethod
    def list(
        cls,
        runtimes: Optional[Sequence[Runtime]] = None,
        simulator_name: Optional[re.Pattern] = None,
        include_unavailable: bool = False,
    ) -> List[Simulator]:
        simulators: List[Simulator] = []
        for runtime_name, devices in cls._list_devices().items():
            runtime = Runtime(runtime_name)
            if runtimes and runtime not in runtimes:
                continue  # Omit this runtime since it was not in the constraints

            _simulators = (Simulator.create(**device, runtime=runtime) for device in devices)
            if not include_unavailable:
                _simulators = (s for s in _simulators if s.is_available)
            if simulator_name:
                _simulators = (s for s in _simulators if simulator_name.search(s.name))
            simulators.extend(_simulators)

        simulators.sort(key=lambda s: (s.runtime, s.name))
        return simulators

    @classmethod
    def get_default(cls) -> Simulator:
        """
        Get default iOS simulator for currently selected Xcode version.
        If available, chooses iPhone SE (2nd generation), otherwise an iPhone or iPad device.
        """
        simulators = Simulator.list(simulator_name=re.compile(r"iPad|iPhone"))

        ios_simulators = [s for s in simulators if s.runtime.runtime_name is Runtime.Name.I_OS]
        if not ios_simulators:
            raise ValueError("No iOS simulators available")
        runtime = sorted({s.runtime for s in ios_simulators}, reverse=True)[0]

        ipads = [s for s in ios_simulators if "iPad" in s.name and s.runtime == runtime]
        iphones = [s for s in ios_simulators if "iPhone" in s.name and s.runtime == runtime]
        if iphones:
            # Choose 2nd gen SE if available
            iphone_se = next((s for s in iphones if s.name == "iPhone SE (2nd generation)"), None)
            simulator = iphone_se or sorted(iphones, key=lambda s: s.name)[-1]
        else:
            simulator = sorted(ipads, key=lambda s: s.name)[-1]
        return simulator

    @classmethod
    def choose_simulator(cls, simulator_description: str, simulators: List[Simulator]) -> Simulator:
        description = simulator_description.strip()
        requested_runtime = Runtime.parse(description)

        if re.match(r"[A-Z0-9-]{36}", description):
            # UDID was given, find matching simulator
            simulator = next((s for s in simulators if s.udid == description), None)
        elif requested_runtime:
            # Runtime constraint was provided, narrow down search domain
            device_name = description.replace(requested_runtime.raw_name, "").strip()
            runtime_choices = (s for s in simulators if s.runtime == requested_runtime and s.name == device_name)
            simulator = next(runtime_choices, None)
        else:
            # Search matching devices by name and choose one with the most recent runtime
            simulator = None
            choices = [s for s in simulators if s.name == description]
            if choices:
                simulator = max(choices, key=lambda s: s.runtime)

        if simulator is None:
            raise ValueError(f"Simulator for destination {description!r} is not available")
        return simulator

    @classmethod
    def find_simulators(cls, simulator_descriptions: Sequence[str]) -> List[Simulator]:
        simulators = cls.list()
        return [cls.choose_simulator(desc, simulators) for desc in simulator_descriptions]

    def get_logs_path(self) -> pathlib.Path:
        return pathlib.Path(f"~/Library/Logs/CoreSimulator/{self.udid}/system.log").expanduser()
