import pytest
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import ProfileType


@pytest.mark.parametrize("profile_type", list(ProfileType))
def test_from_profile_type(profile_type: ProfileType):
    """
    Check that all profile types are mapped to matching certificate type
    """
    certificate_type = CertificateType.from_profile_type(profile_type)
    assert isinstance(certificate_type, CertificateType)
