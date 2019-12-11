from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Union

from codemagic_cli_tools.apple.app_store_connect.resource_manager import ResourceManager
from codemagic_cli_tools.apple.resources import Certificate
from codemagic_cli_tools.apple.resources import CertificateType
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType


class Certificates(ResourceManager):
    """
    Certificates
    https://developer.apple.com/documentation/appstoreconnectapi/certificates
    """

    @property
    def managed_resource(self):
        return Certificate

    @dataclass
    class Filter(ResourceManager.Filter):
        serial_number: Optional[str] = None
        certificate_type: Optional[CertificateType] = None
        display_name: Optional[str] = None

    class Ordering(ResourceManager.Ordering):
        CERTIFICATE_TYPE = 'certificateType'
        DISPLAY_NAME = 'displayName'
        ID = 'id'
        SERIAL_NUMBER = 'serialNumber'

    def create(self, certificate_type: CertificateType, csr_content: str) -> Certificate:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_certificate
        """
        attributes = {
            'certificateType': certificate_type.value,
            'csrContent': csr_content,
        }
        response = self.client.session.post(
            f'{self.client.API_URL}/certificates',
            json=self._get_create_payload(ResourceType.CERTIFICATES, attributes=attributes)
        ).json()
        return Certificate(response['data'], created=True)

    def list(self,
             resource_filter: Filter = Filter(),
             ordering=Ordering.DISPLAY_NAME,
             reverse=False) -> List[Certificate]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_and_download_certificates
        """
        params = {'sort': ordering.as_param(reverse), **resource_filter.as_query_params()}
        certificates = self.client.paginate(f'{self.client.API_URL}/certificates', params=params)
        return [Certificate(certificate) for certificate in certificates]

    def read(self, certificate: Union[LinkedResourceData, ResourceId]) -> Certificate:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_certificate_information
        """
        certificate_id = self._get_resource_id(certificate)
        response = self.client.session.get(f'{self.client.API_URL}/certificates/{certificate_id}').json()
        return Certificate(response['data'])

    def delete(self, certificate: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/revoke_a_certificate
        """
        certificate_id = self._get_resource_id(certificate)
        self.client.session.delete(f'{self.client.API_URL}/certificates/{certificate_id}')
