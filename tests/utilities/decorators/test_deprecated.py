from unittest import mock

import pytest
from codemagic.cli import Colors
from codemagic.utilities.decorators import deprecated


@pytest.fixture
def mock_logger():
    mock_logger = mock.MagicMock()
    with mock.patch("codemagic.utilities.log.get_logger", return_value=mock_logger):
        yield mock_logger


def test_on_function(mock_logger: mock.MagicMock):
    @deprecated(deprecation_version="0.0.1", comment="This is an optional comment.", color=None)
    def function():
        return 1

    assert function.__name__ == "function"
    assert function() == 1
    expected_warning = (
        'Deprecation warning! "function" was deprecated in version 0.0.1 '
        "and is subject for removal in future releases. This is an optional comment."
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


def test_on_static_method(mock_logger: mock.MagicMock):
    class K:
        @staticmethod
        @deprecated(deprecation_version="0.0.1", comment="This is an optional comment.", color=None)
        def static_method():
            return 1

    assert K.static_method.__name__ == "static_method"
    assert K.static_method() == 1
    expected_warning = (
        'Deprecation warning! "K.static_method" was deprecated in version 0.0.1 '
        "and is subject for removal in future releases. This is an optional comment."
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


def test_on_class_method(mock_logger: mock.MagicMock):
    class K:
        @classmethod
        @deprecated(deprecation_version="0.0.1", comment="This is an optional comment.", color=None)
        def class_method(cls):
            return 1

    assert K.class_method.__name__ == "class_method"
    assert K.class_method() == 1
    expected_warning = (
        'Deprecation warning! "K.class_method" was deprecated in version 0.0.1 '
        "and is subject for removal in future releases. This is an optional comment."
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


def test_on_instance_method(mock_logger: mock.MagicMock):
    class K:
        @deprecated(deprecation_version="0.0.1", comment="This is an optional comment.", color=None)
        def instance_method(self):
            return 1

    assert K.instance_method.__name__ == "instance_method"
    assert K().instance_method() == 1
    expected_warning = (
        'Deprecation warning! "K.instance_method" was deprecated in version 0.0.1 '
        "and is subject for removal in future releases. This is an optional comment."
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


@pytest.mark.parametrize(
    ("comment", "expected_comment"),
    (
        (None, ""),
        ("", ""),
        ("Optional comment", " Optional comment"),
    ),
)
def test_comment(comment, expected_comment, mock_logger: mock.MagicMock):
    @deprecated("0.0.0", comment=comment, color=None)
    def f():
        pass

    f()
    expected_warning = (
        'Deprecation warning! "f" was deprecated in version 0.0.0 '
        f"and is subject for removal in future releases.{expected_comment}"
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


def test_default_color(mock_logger: mock.MagicMock):
    @deprecated("0.0.0")
    def f():
        pass

    f()
    expected_warning = Colors.YELLOW(
        'Deprecation warning! "f" was deprecated in version 0.0.0 and is subject for removal in future releases.',
    )
    mock_logger.warning.assert_called_once_with(expected_warning)


def test_color(mock_logger: mock.MagicMock):
    @deprecated("0.0.0", color=Colors.BLUE)
    def f():
        pass

    f()
    expected_warning = Colors.BLUE(
        'Deprecation warning! "f" was deprecated in version 0.0.0 and is subject for removal in future releases.',
    )
    mock_logger.warning.assert_called_once_with(expected_warning)
