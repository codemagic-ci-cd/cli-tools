import pytest

from apple.resources import Certificate
from apple.resources import CertificateType
from apple.resources import ResourceId
from apple.resources import ResourceType
from tests.apple.app_store_connect_api_client.endpoint_tests_base import EndpointTestsBase


@pytest.mark.skip(reason='Live App Store Connect API access')
class CertificateEndpointsTest(EndpointTestsBase):

    def test_list_certificates(self):
        expected_type = CertificateType.IOS_DEVELOPMENT
        certificates = self.api_client.list_certificates(filter_certificate_type=expected_type)
        assert len(certificates) > 0
        for certificate in certificates:
            assert isinstance(certificate, Certificate)
            assert certificate.type is ResourceType.CERTIFICATES
            assert certificate.attributes.certificateType is expected_type

    def test_read_certificate(self):
        certificate_id = ResourceId('X6NCZS3K2D')
        certificate = self.api_client.read_certificate(certificate_id)
        assert isinstance(certificate, Certificate)
        assert certificate.id == certificate_id
        assert certificate.type is ResourceType.CERTIFICATES
