import pytest

from codemagic_cli_tools.apple.resources import Certificate as CertificateResource
from codemagic_cli_tools.apple.resources import CertificateType
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import PrivateKey
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_unencrypted_pem')
class CertificatesTest(ResourceManagerTestsBase):

    def test_create(self):
        rsa = PrivateKey.pem_to_rsa(self.unencrypted_pem.content)
        csr = Certificate.create_certificate_signing_request(rsa)
        csr_content = Certificate.get_certificate_signing_request_content(csr)
        certificate = self.api_client.certificates.create(CertificateType.IOS_DEVELOPMENT, csr_content)
        assert isinstance(certificate, CertificateResource)
        assert certificate.attributes.displayName == 'Created via API'
        assert certificate.type is ResourceType.CERTIFICATES

    def test_list(self):
        expected_type = CertificateType.IOS_DEVELOPMENT
        certificates_filter = self.api_client.certificates.Filter(certificate_type=expected_type)
        certificates = self.api_client.certificates.list(resource_filter=certificates_filter)
        assert len(certificates) > 0
        for certificate in certificates:
            assert isinstance(certificate, CertificateResource)
            assert certificate.type is ResourceType.CERTIFICATES
            assert certificate.attributes.certificateType is expected_type

    def test_read(self):
        certificate_id = ResourceId('X6NCZS3K2D')
        certificate = self.api_client.certificates.read(certificate_id)
        assert isinstance(certificate, CertificateResource)
        assert certificate.id == certificate_id
        assert certificate.type is ResourceType.CERTIFICATES

    def test_revoke(self):
        certificate_id = ResourceId('A7N37QDAWK')
        self.api_client.certificates.delete(certificate_id)
