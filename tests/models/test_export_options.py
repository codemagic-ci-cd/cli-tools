import logging
import plistlib
import tempfile
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from unittest import mock

import pytest
from codemagic.cli import Colors
from codemagic.models import ExportOptions
from codemagic.models.export_options import ProvisioningProfileInfo

mock_logger = mock.Mock(spec=logging.Logger)


def test_export_options_initialize_from_path(export_options_list_path, export_options_dict):
    export_options = ExportOptions.from_path(export_options_list_path)
    assert export_options.dict() == export_options_dict


def test_export_options_initialize_from_missing_path():
    with NamedTemporaryFile(suffix=".plist") as tf:
        plist_path = tf.name
    with pytest.raises(FileNotFoundError):
        ExportOptions.from_path(plist_path)


def test_export_options_initialize_from_dir_path():
    with TemporaryDirectory(suffix=".plist") as td:
        with pytest.raises(FileNotFoundError):
            ExportOptions.from_path(td)


def test_export_options_initialize_from_path_invalid_contents():
    with NamedTemporaryFile(suffix=".plist") as tf:
        tf.write(b"this is not a valid property list")
        tf.flush()
        with pytest.raises(ValueError):
            ExportOptions.from_path(tf.name)


def test_export_options_initialize(export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    assert export_options.dict() == export_options_dict


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("manageAppVersionAndBuildNumber", True),
        ("manageAppVersionAndBuildNumber", False),
        ("signingCertificate", "Certificate name"),
        ("iCloudContainerEnvironment", "environment"),
    ],
)
def test_export_options_initialize_extra_values(field_name, value, export_options_dict):
    given_export_options = {**export_options_dict, field_name: value}
    export_options = ExportOptions(**given_export_options)
    assert export_options.dict() == given_export_options


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("manageAppVersionAndBuildNumber", True),
        ("manageAppVersionAndBuildNumber", False),
        ("signingCertificate", "Certificate name"),
        ("iCloudContainerEnvironment", "environment"),
    ],
)
def test_export_options_set_valid_values(field_name, value, export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    export_options.set_value(field_name=field_name, value=value)
    assert export_options.dict() == {**export_options_dict, field_name: value}


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("manifest", ""),
        ("manifest", 1),
        ("manifest", 3.4),
        ("manifest", {"invalid_key": 1}),
        ("provisioningProfiles", [1]),
        ("provisioningProfiles", [ProvisioningProfileInfo("bundle_id", "name"), {"k": "v"}]),
        ("method", "invalid method"),
        ("destination", "invalid destination"),
        ("teamID", -1),
        ("teamID", True),
        ("stripSwiftSymbols", "false"),
        ("stripSwiftSymbols", "YES"),
    ],
)
def test_export_options_set_invalid_values(field_name, value, export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    with pytest.raises(ValueError):
        export_options.set_value(field_name=field_name, value=value)


@mock.patch("codemagic.models.export_options.log.get_logger", new=mock.Mock(return_value=mock_logger))
def test_export_options_set_unknown_fields():
    export_options = ExportOptions()
    export_options.set_value(field_name="unknownExportOption", value=False)

    expected_warning = 'Warning: Using unknown export option "unknownExportOption"'
    mock_logger.warning.assert_called_once_with(Colors.YELLOW(expected_warning))
    assert export_options.dict() == {"unknownExportOption": False}


@mock.patch("codemagic.models.export_options.log.get_logger", new=mock.Mock(return_value=mock_logger))
def test_export_options_unknown_fields_notify():
    export_options = ExportOptions()
    export_options.set_value(field_name="unknownExportOption", value=False)
    export_options.notify("Title")

    mock_logger.info.assert_has_calls(
        [
            mock.call("Title"),
            mock.call(Colors.BLUE(" - Unknown Export Option: False")),
        ],
    )


def test_export_options_unknown_fields_from_path():
    expected_export_options = {
        "signingStyle": "manual",  # Known field
        "unknownExportOption": False,  # Unknown field
    }

    with tempfile.NamedTemporaryFile(mode="wb") as tf:
        tf.write(plistlib.dumps(expected_export_options))
        tf.flush()
        export_options = ExportOptions.from_path(tf.name)

    assert export_options.dict() == expected_export_options
