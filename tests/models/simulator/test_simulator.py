import json
import pathlib
from typing import Dict
from typing import Union

import pytest

from codemagic.models.simulator import Simulator


@pytest.fixture
def simulator_mock() -> Dict[str, Union[str, bool]]:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'simulator.json'
    with mock_path.open() as fd:
        return json.load(fd)


def test_create_simulator(simulator_mock):
    simulator = Simulator.create(**simulator_mock)
    assert simulator.udid == '7D9D6930-90D9-453A-BF11-63C5CA9CDA15'
    assert simulator.is_available is True
    assert simulator.state == 'Shutdown'
    assert simulator.name == 'iPad Air (3rd generation)'
    assert simulator.data_path == pathlib.Path('/path/to/simulator/data')
    assert simulator.log_path == pathlib.Path('/path/to/simulator/logs')
    print(simulator.dict())


def test_dict_serialization(simulator_mock):
    simulator = Simulator.create(**simulator_mock)
    assert simulator.dict() == {
        'udid': '7D9D6930-90D9-453A-BF11-63C5CA9CDA15',
        'is_available': True,
        'state': 'Shutdown',
        'name': 'iPad Air (3rd generation)',
        'data_path': '/path/to/simulator/data',
        'log_path': '/path/to/simulator/logs',
    }
