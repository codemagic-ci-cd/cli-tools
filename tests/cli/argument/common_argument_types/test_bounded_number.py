from argparse import ArgumentTypeError

import pytest
from codemagic.cli.argument import CommonArgumentTypes


@pytest.mark.parametrize(
    ("number_as_string", "requested_type", "expected_number"),
    (
        ("1", int, 1),
        ("1.0", float, 1.0),
        ("2", int, 2),
        ("2", float, 2.0),
    ),
)
def test_successful_conversion(number_as_string, requested_type, expected_number):
    constructor = CommonArgumentTypes.bounded_number(requested_type, -100, 100, inclusive=True)
    resolved_number = constructor(number_as_string)
    assert isinstance(resolved_number, requested_type)
    assert resolved_number == expected_number


@pytest.mark.parametrize(
    ("invalid_number_input", "requested_type", "expected_error_message"),
    (
        ("1.0", int, "Value 1.0 is not a valid integer"),
        ("a", int, "Value a is not a valid integer"),
        ("?", int, "Value ? is not a valid integer"),
        ("?", float, "Value ? is not a valid floating point number"),
        ("x", float, "Value x is not a valid floating point number"),
    ),
)
def test_invalid_input(invalid_number_input, requested_type, expected_error_message):
    constructor = CommonArgumentTypes.bounded_number(requested_type, -100, 100, inclusive=True)
    with pytest.raises(ArgumentTypeError) as error_info:
        constructor(invalid_number_input)
    assert str(error_info.value) == expected_error_message


@pytest.mark.parametrize(
    ("number_as_string", "inclusive_comparison", "expected_number"),
    (
        ("1", True, 1),
        ("10", True, 10),
        ("2", False, 2),
        ("9", False, 9),
    ),
)
def test_within_bounds(number_as_string, inclusive_comparison, expected_number):
    constructor = CommonArgumentTypes.bounded_number(int, 1, 10, inclusive=inclusive_comparison)
    resolved_value = constructor(number_as_string)
    assert resolved_value == expected_number


@pytest.mark.parametrize(
    ("out_of_bounds_number_string", "inclusive_comparison"),
    (
        ("-1", True),
        ("0", True),
        ("11", True),
        ("20", True),
        ("-1", False),
        ("1", False),
        ("10", False),
        ("11", False),
        ("20", False),
    ),
)
def test_out_of_bounds(out_of_bounds_number_string, inclusive_comparison):
    constructor = CommonArgumentTypes.bounded_number(int, 1, 10, inclusive=inclusive_comparison)
    with pytest.raises(ArgumentTypeError) as error_info:
        constructor(out_of_bounds_number_string)

    comparison_op = "<=" if inclusive_comparison else "<"
    expected_error_message = (
        f"Value {out_of_bounds_number_string} is out of allowed bounds, 1 {comparison_op} value {comparison_op} 10"
    )
    assert str(error_info.value) == expected_error_message
