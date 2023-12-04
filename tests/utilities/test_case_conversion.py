import pytest
from codemagic.utilities import case_conversion


@pytest.mark.parametrize(
    ("snake_case_input", "expected_camel_case_output"),
    [
        ("", ""),
        ("word", "word"),
        ("_word", "Word"),
        ("snake_case", "snakeCase"),
        ("snake_case_", "snakeCase_"),
        ("snake_case_ snakeCase", "snakeCase_ snakeCase"),
        ("a_b_c_d_e_f", "aBCDEF"),
    ],
)
def test_snake_case_to_camel_case(snake_case_input, expected_camel_case_output):
    converted_input = case_conversion.snake_to_camel(snake_case_input)
    assert converted_input == expected_camel_case_output


@pytest.mark.parametrize(
    ("camel_case_input", "expected_snake_case_output"),
    [
        ("", ""),
        ("word", "word"),
        ("Word", "word"),
        ("camelCase", "camel_case"),
        ("camelCase_", "camel_case_"),
        ("camelCase_ camelCase", "camel_case_ camel_case"),
        ("camelCase snake_case", "camel_case snake_case"),
        ("aBCDEF", "a_b_c_d_e_f"),
    ],
)
def test_camel_case_to_snake_case(camel_case_input, expected_snake_case_output):
    converted_input = case_conversion.camel_to_snake(camel_case_input)
    assert converted_input == expected_snake_case_output
