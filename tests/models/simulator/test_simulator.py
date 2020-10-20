import json
import pathlib
from typing import Dict
from typing import List
from typing import Union
from unittest import mock

import pytest

from codemagic.models.simulator import Runtime
from codemagic.models.simulator import Simulator


@pytest.fixture
def simulator_mock() -> Dict[str, Union[str, bool]]:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'simulator.json'
    with mock_path.open() as fd:
        return json.load(fd)


def mock_list_devices(*_args) -> Dict[str, List[Dict]]:
    mock_path = pathlib.Path(__file__).parent / 'mocks' / 'devices.json'
    with mock_path.open() as fd:
        return json.load(fd)['devices']


def test_create_simulator(simulator_mock):
    runtime = Runtime('iOS 12.4')
    simulator = Simulator.create(**simulator_mock, runtime=runtime)
    assert simulator.udid == '7D9D6930-90D9-453A-BF11-63C5CA9CDA15'
    assert simulator.is_available is True
    assert simulator.state == 'Shutdown'
    assert simulator.name == 'iPad Air (3rd generation)'
    assert simulator.data_path == pathlib.Path('/path/to/simulator/data')
    assert simulator.log_path == pathlib.Path('/path/to/simulator/logs')
    assert simulator.runtime == runtime


def test_dict_serialization(simulator_mock):
    simulator = Simulator.create(**simulator_mock, runtime=Runtime('iOS 12.4'))
    assert simulator.dict() == {
        'udid': '7D9D6930-90D9-453A-BF11-63C5CA9CDA15',
        'is_available': True,
        'state': 'Shutdown',
        'name': 'iPad Air (3rd generation)',
        'data_path': '/path/to/simulator/data',
        'log_path': '/path/to/simulator/logs',
        'runtime': 'iOS 12.4',
    }


@pytest.mark.parametrize('test_destination, expected_udid', [
    ('iOS 12.4 iPad Air (3rd generation)', '2F47FEEB-5BA8-4829-A4FA-591C0B4654C4'),
    ('iPad Air (3rd generation) iOS 12.4', '2F47FEEB-5BA8-4829-A4FA-591C0B4654C4'),
    ('iPhone 8', '87895091-1524-455B-A549-12ADED0AD7F0'),
    ('BB6C80AD-3E47-4040-90AB-2F8FFEA6F8FC', 'BB6C80AD-3E47-4040-90AB-2F8FFEA6F8FC'),
    ('Apple Watch Series 5 - 44mm', '8E76B1FD-B5CE-48A2-BBD7-39A4D389234D'),
    ('watchOS 7.0 Apple Watch Series 5 - 40mm', '478AA391-641E-4D2C-9E4E-E90770A69C36'),
])
@mock.patch.object(Simulator, '_list_devices', mock_list_devices)
def test_choose_simulator(test_destination, expected_udid):
    simulator = Simulator.choose_simulator(test_destination, Simulator.list())
    assert simulator.udid == expected_udid


@mock.patch.object(Simulator, '_list_devices', mock_list_devices)
def test_choose_simulator_not_found():
    description = 'Samsung Galaxy S20'
    with pytest.raises(ValueError) as exception_info:
        Simulator.choose_simulator(description, Simulator.list())
    assert description in str(exception_info.value)
