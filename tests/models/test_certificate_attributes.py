import pytest

from codemagic.models import CertificateAttributes


@pytest.mark.parametrize('certificate_attributes, expected_components', [
    (CertificateAttributes(), []),
    (CertificateAttributes(common_name='Common name'), [('CN', 'Common name')]),
    (CertificateAttributes(common_name='C N', locality='Locality'), [('CN', 'C N'), ('L', 'Locality')]),
    (CertificateAttributes(country='Country', locality='Locality'), [('L', 'Locality'), ('C', 'Country')]),
])
def test_get_components(certificate_attributes, expected_components):
    assert certificate_attributes.get_components() == expected_components


@pytest.mark.parametrize('distinguished_name, expected_certificate_attributes', [
    (
            'CN=Sample Cert, OU=R&D, O=Company Ltd., L=Dublin 4, S=Dublin, C=IE',
            CertificateAttributes(
                common_name='Sample Cert',
                organizational_unit='R&D',
                organization='Company Ltd.',
                locality='Dublin 4',
                state_or_province='Dublin',
                country='IE',
            ),
    ),
    ('S=Dublin, C=IE', CertificateAttributes(state_or_province='Dublin', country='IE')),
    ('S=Dublin,C=IE', CertificateAttributes(state_or_province='Dublin', country='IE')),
    ('CN=Sample Cert, C=EE', CertificateAttributes(common_name='Sample Cert', country='EE')),
    ('CN=Sample Cert,C=EE', CertificateAttributes(common_name='Sample Cert', country='EE')),
    (
            'CN=Sample Cert, O=Company,C=EE',
            CertificateAttributes(common_name='Sample Cert', organization='Company', country='EE'),
    ),
])
def test_from_distinguished_name(distinguished_name, expected_certificate_attributes):
    certificate_attributes = CertificateAttributes.from_distinguished_name(distinguished_name)
    assert certificate_attributes == expected_certificate_attributes
    assert certificate_attributes.is_valid() is True


def test_from_empty_distinguished_name():
    certificate_attributes = CertificateAttributes.from_distinguished_name('')
    assert certificate_attributes.get_components() == []
    assert certificate_attributes.is_valid() is False


@pytest.mark.parametrize('certificate_attributes, expected_distinguished_name', [
    (
            CertificateAttributes(
                common_name='Sample Cert',
                organizational_unit='R&D',
                organization='Company Ltd.',
                locality='Dublin 4',
                state_or_province='Dublin',
                country='IE',
            ),
            'CN=Sample Cert,OU=R&D,O=Company Ltd.,L=Dublin 4,S=Dublin,C=IE',
    ),
    (CertificateAttributes(state_or_province='Dublin', country='IE'), 'S=Dublin,C=IE'),
    (CertificateAttributes(common_name='Sample Cert', country='EE'), 'CN=Sample Cert,C=EE'),
    (
            CertificateAttributes(common_name='Sample Cert', organization='Company', country='EE'),
            'CN=Sample Cert,O=Company,C=EE',
    ),
])
def test_get_distinguished_name(certificate_attributes, expected_distinguished_name):
    distinguished_name = certificate_attributes.get_distinguished_name()
    assert distinguished_name == expected_distinguished_name
