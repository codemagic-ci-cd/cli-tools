import os

import pytest

from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ResourceType
from codemagic.apple.resources import SigningCertificate
from codemagic.models import Certificate
from codemagic.models import PrivateKey
from tests.apple.app_store_connect.resource_manager_test_base import ResourceManagerTestsBase


@pytest.mark.skipif(not os.environ.get('RUN_LIVE_API_TESTS'), reason='Live App Store Connect API access')
@pytest.mark.usefixtures('class_unencrypted_pem')
class CertificatesTest(ResourceManagerTestsBase):

    def test_create(self):
        private_key = PrivateKey.from_pem(self.unencrypted_pem.content)
        csr = Certificate.create_certificate_signing_request(private_key)
        csr_content = Certificate.get_certificate_signing_request_content(csr)
        certificate = self.api_client.signing_certificates.create(CertificateType.IOS_DEVELOPMENT, csr_content)
        assert isinstance(certificate, SigningCertificate)
        assert certificate.attributes.displayName == 'Created via API'
        assert certificate.type is ResourceType.CERTIFICATES

    def test_list(self):
        expected_type = CertificateType.IOS_DEVELOPMENT
        certificates_filter = self.api_client.signing_certificates.Filter(certificate_type=expected_type)
        certificates = self.api_client.signing_certificates.list(resource_filter=certificates_filter)
        assert len(certificates) > 0
        for certificate in certificates:
            assert isinstance(certificate, SigningCertificate)
            assert certificate.type is ResourceType.CERTIFICATES
            assert certificate.attributes.certificateType is expected_type

    def test_read(self):
        certificate_id = ResourceId('X6NCZS3K2D')
        certificate = self.api_client.signing_certificates.read(certificate_id)
        assert isinstance(certificate, SigningCertificate)
        assert certificate.id == certificate_id
        assert certificate.type is ResourceType.CERTIFICATES

    def test_revoke(self):
        certificate_id = ResourceId('A7N37QDAWK')
        self.api_client.signing_certificates.delete(certificate_id)
