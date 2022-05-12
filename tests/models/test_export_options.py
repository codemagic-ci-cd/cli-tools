from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory

import pytest

from codemagic.models import ExportOptions
from codemagic.models.export_options import ProvisioningProfileInfo


def test_export_options_initialize_from_path(export_options_list_path, export_options_dict):
    export_options = ExportOptions.from_path(export_options_list_path)
    assert export_options.dict() == export_options_dict


def test_export_options_initialize_from_missing_path():
    with NamedTemporaryFile(suffix='.plist') as tf:
        plist_path = tf.name
    with pytest.raises(FileNotFoundError):
        ExportOptions.from_path(plist_path)


def test_export_options_initialize_from_dir_path():
    with TemporaryDirectory(suffix='.plist') as td:
        with pytest.raises(FileNotFoundError):
            ExportOptions.from_path(td)


def test_export_options_initialize_from_path_invalid_contents():
    with NamedTemporaryFile(suffix='.plist') as tf:
        tf.write(b'this is not a valid property list')
        tf.flush()
        with pytest.raises(ValueError):
            ExportOptions.from_path(tf.name)


def test_export_options_initialize(export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    assert export_options.dict() == export_options_dict


@pytest.mark.parametrize('field_name, value', [
    ('manageAppVersionAndBuildNumber', True),
    ('manageAppVersionAndBuildNumber', False),
    ('signingCertificate', 'Certificate name'),
    ('iCloudContainerEnvironment', 'environment'),
])
def test_export_options_initialize_extra_values(field_name, value, export_options_dict):
    given_export_options = {**export_options_dict, field_name: value}
    export_options = ExportOptions(**given_export_options)
    assert export_options.dict() == given_export_options


@pytest.mark.parametrize('field_name, value', [
    ('manageAppVersionAndBuildNumber', True),
    ('manageAppVersionAndBuildNumber', False),
    ('signingCertificate', 'Certificate name'),
    ('iCloudContainerEnvironment', 'environment'),
])
def test_export_options_set_valid_values(field_name, value, export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    export_options.set_value(field_name=field_name, value=value)
    assert export_options.dict() == {**export_options_dict, field_name: value}


@pytest.mark.parametrize('field_name, value', [
    ('manifest', ''),
    ('manifest', 1),
    ('manifest', 3.4),
    ('manifest', {'invalid_key': 1}),
    ('invalid_field', -1),
    ('provisioningProfiles', [1]),
    ('provisioningProfiles', [ProvisioningProfileInfo('bundle_id', 'name'), {'k': 'v'}]),
    ('method', 'invalid method'),
    ('destination', 'invalid destination'),
])
def test_export_options_set_invalid_values(field_name, value, export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    with pytest.raises(ValueError):
        export_options.set_value(field_name=field_name, value=value)
