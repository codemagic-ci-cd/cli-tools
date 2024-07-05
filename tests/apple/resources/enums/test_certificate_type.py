from typing import List
from typing import Sequence

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


@pytest.mark.parametrize("certificate_type", list(CertificateType))
def test_resolve_applicable_types_using_literal_certificate_type(certificate_type: CertificateType):
    """
    Check that type can be resolved when CertificateType literal instance is passed via
    `certificate_types` keyword argument. Expected result is to have a list that contains
    only the passed type.
    """
    resolved_types = CertificateType.resolve_applicable_types(certificate_types=certificate_type)
    assert resolved_types == [certificate_type]


@pytest.mark.parametrize(
    "certificate_types",
    (
        (CertificateType.IOS_DISTRIBUTION,),
        (CertificateType.IOS_DISTRIBUTION, CertificateType.IOS_DEVELOPMENT),
        [CertificateType.IOS_DISTRIBUTION, CertificateType.IOS_DEVELOPMENT],
        [CertificateType.MAC_APP_DEVELOPMENT, CertificateType.MAC_APP_DISTRIBUTION],
        [
            CertificateType.MAC_APP_DEVELOPMENT,
            CertificateType.MAC_INSTALLER_DISTRIBUTION,
            CertificateType.MAC_APP_DISTRIBUTION,
        ],
    ),
)
def test_resolve_applicable_types_using_multiple_certificate_types(certificate_types: Sequence[CertificateType]):
    """
    Check that type can be resolved when number of CertificateType instances are passed via
    `certificate_types` keyword argument as a sequence. Expected result is to have a list that
    contains all the passed types without duplicates and nothing else.
    """
    resolved_types = CertificateType.resolve_applicable_types(certificate_types=certificate_types)
    assert resolved_types == list(certificate_types)


def test_resolve_applicable_types_using_multiple_certificate_types_omit_duplicates():
    """
    Check that duplicates are removed from given certificate types when resolving result.
    Return value should contain each resolved type only once and in the order in which they
    appeared first.
    """
    resolved_types = CertificateType.resolve_applicable_types(
        certificate_types=[
            CertificateType.MAC_INSTALLER_DISTRIBUTION,
            CertificateType.MAC_APP_DEVELOPMENT,
            CertificateType.MAC_APP_DEVELOPMENT,
            CertificateType.MAC_INSTALLER_DISTRIBUTION,
            CertificateType.MAC_APP_DEVELOPMENT,
            CertificateType.MAC_APP_DISTRIBUTION,
        ],
    )
    assert resolved_types == [
        CertificateType.MAC_INSTALLER_DISTRIBUTION,
        CertificateType.MAC_APP_DEVELOPMENT,
        CertificateType.MAC_APP_DISTRIBUTION,
    ]


@pytest.mark.parametrize(
    ("profile_type", "expected_certificate_type"),
    (
        (ProfileType.IOS_APP_DEVELOPMENT, CertificateType.IOS_DEVELOPMENT),
        (ProfileType.IOS_APP_INHOUSE, CertificateType.DISTRIBUTION),
        (ProfileType.MAC_APP_DEVELOPMENT, CertificateType.MAC_APP_DEVELOPMENT),
        (ProfileType.MAC_CATALYST_APP_DEVELOPMENT, CertificateType.DEVELOPMENT),
        (ProfileType.MAC_CATALYST_APP_STORE, CertificateType.DISTRIBUTION),
        (ProfileType.TVOS_APP_ADHOC, CertificateType.DISTRIBUTION),
        (ProfileType.TVOS_APP_DEVELOPMENT, CertificateType.DEVELOPMENT),
        (ProfileType.TVOS_APP_INHOUSE, CertificateType.DISTRIBUTION),
        (ProfileType.TVOS_APP_STORE, CertificateType.DISTRIBUTION),
    ),
)
def test_resolve_applicable_types_using_profile_type_with_one_match(
    profile_type: ProfileType,
    expected_certificate_type: CertificateType,
):
    """
    Most provisioning profile types are in one-to-one correspondence with a certain
    certificate type. Check that expected certificate type is resolved for such profiles,
    and nothing else.
    """
    resolved_types = CertificateType.resolve_applicable_types(profile_type=profile_type)
    assert resolved_types == [expected_certificate_type]


@pytest.mark.parametrize(
    ("profile_type", "expected_certificate_types"),
    (
        (
            ProfileType.IOS_APP_ADHOC,
            [CertificateType.DISTRIBUTION, CertificateType.IOS_DISTRIBUTION],
        ),
        (
            ProfileType.IOS_APP_STORE,
            [CertificateType.DISTRIBUTION, CertificateType.IOS_DISTRIBUTION],
        ),
        (
            ProfileType.MAC_APP_DIRECT,
            [CertificateType.DEVELOPER_ID_APPLICATION, CertificateType.DEVELOPER_ID_APPLICATION_G2],
        ),
        (
            ProfileType.MAC_CATALYST_APP_DIRECT,
            [CertificateType.DEVELOPER_ID_APPLICATION, CertificateType.DEVELOPER_ID_APPLICATION_G2],
        ),
        (
            ProfileType.MAC_APP_STORE,
            [CertificateType.DISTRIBUTION, CertificateType.MAC_APP_DISTRIBUTION],
        ),
    ),
)
def test_resolve_applicable_types_using_profile_type_with_many_matches(
    profile_type: ProfileType,
    expected_certificate_types: List[CertificateType],
):
    """
    Some provisioning profile types can be used with more than one type of certificates.
    Check that for those profile types all the allowed certificate types are resolved,
    and nothing else. Additionally, the secondary resolved type should be always last.
    """
    resolved_types = CertificateType.resolve_applicable_types(profile_type=profile_type)
    assert resolved_types == expected_certificate_types


def test_resolve_applicable_types_with_multiple_arguments():
    """
    Check that when different arguments are passed to the resolver at once, then
    all of them are respected and used accordingly.
    """
    resolved_types = CertificateType.resolve_applicable_types(
        profile_type=ProfileType.IOS_APP_STORE,
        certificate_types=[
            CertificateType.DEVELOPER_ID_APPLICATION,
            CertificateType.DEVELOPER_ID_APPLICATION_G2,
        ],
    )
    expected_certificate_types = [
        CertificateType.DEVELOPER_ID_APPLICATION,  # From "certificate_types" argument
        CertificateType.DEVELOPER_ID_APPLICATION_G2,  # From "certificate_types" argument
        CertificateType.DISTRIBUTION,  # From given profile type
        CertificateType.IOS_DISTRIBUTION,  # From given profile type
    ]
    assert resolved_types == expected_certificate_types
