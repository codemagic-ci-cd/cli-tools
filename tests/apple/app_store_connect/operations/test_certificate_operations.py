import pytest
from cryptography.hazmat.primitives import serialization

from codemagic_cli_tools.apple.resources import Certificate as CertificateResource
from codemagic_cli_tools.apple.resources import CertificateType
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType
from codemagic_cli_tools.models import Certificate
from codemagic_cli_tools.models import PrivateKey
from tests.apple.app_store_connect.operations.operations_test_base import OperationsTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_unencrypted_pem')
class CertificateOperationsTest(OperationsTestsBase):

    def test_create(self):
        rsa = PrivateKey.pem_to_rsa(self.unencrypted_pem.content)
        csr = Certificate.create_certificate_signing_request(rsa)
        csr_content = csr.public_bytes(serialization.Encoding.PEM)
        certificate = self.api_client.certificates.create(CertificateType.IOS_DEVELOPMENT, csr_content)
        assert isinstance(certificate, CertificateResource)
        assert certificate.attributes.displayName == 'Created via API'
        assert certificate.type is ResourceType.CERTIFICATES

    def test_list(self):
        expected_type = CertificateType.IOS_DEVELOPMENT
        certificates = self.api_client.certificates.list(filter_certificate_type=expected_type)
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
        self.api_client.certificates.revoke(certificate_id)
