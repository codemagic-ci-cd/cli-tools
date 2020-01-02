import pytest

from codemagic_cli_tools.models import ExportOptions
from codemagic_cli_tools.models.export_options import ProvisioningProfileInfo


def test_export_options_initialize_from_path(export_options_list_path, export_options_dict):
    export_options = ExportOptions.from_path(export_options_list_path)
    assert export_options.dict() == export_options_dict


def test_export_options_initialize(export_options_dict):
    export_options = ExportOptions(**export_options_dict)
    assert export_options.dict() == export_options_dict


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
    with pytest.raises(ValueError) as error_info:
        export_options.set_value(field_name=field_name, value=value)
    print(error_info)
