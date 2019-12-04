import enum
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Optional

import pytest

from codemagic_cli_tools.apple.app_store_connect.resource_manager import ResourceManager

NOW = datetime(year=2019, month=8, day=20)
UTC_NOW = datetime(year=2019, month=8, day=20, tzinfo=timezone.utc)


class StubEnum(enum.Enum):
    A = 'a'
    B = 'b'


@dataclass
class StubFilter(ResourceManager.Filter):
    field_one: Optional[str] = None
    field_two: Optional[StubEnum] = None
    field_three_four: Optional[str] = None


@pytest.mark.parametrize('filter_params, expected_query_params', [
    ({'field_one': '1'}, {'filter[fieldOne]': '1'}),
    ({'field_two': '2'}, {'filter[fieldTwo]': '2'}),
    ({'field_three_four': '34'}, {'filter[fieldThreeFour]': '34'}),
    ({'field_one': '1', 'field_two': None}, {'filter[fieldOne]': '1'}),
    ({'field_two': '2', 'field_one': None}, {'filter[fieldTwo]': '2'}),
    ({'field_three_four': '34', 'field_one': None, 'field_two': None}, {'filter[fieldThreeFour]': '34'}),
    ({'field_one': '1', 'field_two': '2'}, {'filter[fieldOne]': '1', 'filter[fieldTwo]': '2'}),
])
def test_resource_manager_filter_to_params_conversion(filter_params, expected_query_params):
    test_filter = StubFilter(**filter_params)
    assert test_filter.as_query_params() == expected_query_params


@pytest.mark.parametrize('snake_case_input, expected_camel_case_output', [
    ('', ''),
    ('word', 'word'),
    ('_word', 'Word'),
    ('snake_case', 'snakeCase'),
    ('snake_case_', 'snakeCase_'),
    ('snake_case_ snakeCase', 'snakeCase_ snakeCase'),
    ('a_b_c_d_e_f', 'aBCDEF'),
])
def test_resource_manager_filter_camel_case_converter(snake_case_input, expected_camel_case_output):
    converted_input = ResourceManager.Filter._snake_to_camel(snake_case_input)
    assert converted_input == expected_camel_case_output
