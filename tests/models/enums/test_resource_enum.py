import pytest

from codemagic.models.enums import ResourceEnum
from codemagic.models.enums import ResourceEnumMeta


class MockEnum(ResourceEnum):
    A = 'A'
    B = 'B'


@pytest.mark.parametrize('enum_value', MockEnum.__members__.keys())
def test_resource_enum(enum_value):
    mock_enum = MockEnum(enum_value)
    assert isinstance(mock_enum, MockEnum)
    assert mock_enum.value == enum_value


@pytest.mark.parametrize('enum_value', ('C', 'D', 'Lorem ipsum'))
def test_resource_enum_graceful_fallback_on_strings(enum_value):
    mock_enum = MockEnum(enum_value)
    assert not isinstance(mock_enum, MockEnum)
    assert MockEnum.__name__ in mock_enum.__class__.__name__
    assert mock_enum.value == enum_value


@pytest.mark.parametrize('enum_value', ((1, 2), 3.5, None, 4, 5, [], {}))
def test_resource_enum_graceful_fallback_invalid_inputs(enum_value):
    with pytest.raises(ValueError):
        MockEnum(enum_value)


@pytest.mark.parametrize('enum_value', ('C', 'D', 'Lorem ipsum'))
def test_resource_enum_graceful_fallback_disabled(enum_value):
    ResourceEnumMeta.graceful_fallback = False
    with pytest.raises(ValueError):
        MockEnum(enum_value)
    ResourceEnumMeta.graceful_fallback = True


@pytest.mark.parametrize('is_graceful_before', [True, False])
def test_context_manager(is_graceful_before):
    ResourceEnumMeta.graceful_fallback = is_graceful_before
    with ResourceEnumMeta.without_graceful_fallback():
        with pytest.raises(ValueError):
            MockEnum('invalid value')
    assert ResourceEnumMeta.graceful_fallback is is_graceful_before
