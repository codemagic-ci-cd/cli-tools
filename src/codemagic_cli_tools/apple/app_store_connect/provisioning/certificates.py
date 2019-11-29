from typing import List, AnyStr
from typing import Optional
from typing import Union

from codemagic_cli_tools.apple.app_store_connect.resource_manager import ResourceManager
from codemagic_cli_tools.apple.resources import Certificate
from codemagic_cli_tools.apple.resources import CertificateType
from codemagic_cli_tools.apple.resources import LinkedResourceData
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.apple.resources import ResourceType


class CertificateOrdering(ResourceManager.Ordering):
    CERTIFICATE_TYPE = 'certificateType'
    DISPLAY_NAME = 'displayName'
    ID = 'id'
    SERIAL_NUMBER = 'serialNumber'


class Certificates(ResourceManager):
    """
    Certificates
    https://developer.apple.com/documentation/appstoreconnectapi/certificates
    """

    def create(self, certificate_type: CertificateType, csr_content: AnyStr):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_certificate
        """
        if isinstance(csr_content, bytes):
            content = csr_content.decode()
        else:
            content = csr_content
        attributes = {
            'certificateType': certificate_type.value,
            'csrContent': content,
        }
        response = self.client.session.post(
            f'{self.client.API_URL}/certificates',
            json=self.client.get_create_payload(ResourceType.CERTIFICATES, attributes=attributes)
        ).json()
        return Certificate(response['data'])

    def list(self,
             filter_certificate_type: Optional[CertificateType] = None,
             filter_display_name: Optional[str] = None,
             ordering=CertificateOrdering.DISPLAY_NAME,
             reverse=False) -> List[Certificate]:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/list_and_download_certificates
        """
        params = {'sort': ordering.as_param(reverse)}
        if filter_certificate_type is not None:
            params['filter[certificateType]'] = filter_certificate_type.value
        if filter_display_name is not None:
            params['filter[displayName]'] = filter_display_name

        certificates = self.client.paginate(f'{self.client.API_URL}/certificates', params=params)
        return [Certificate(certificate) for certificate in certificates]

    def read(self, resource: Union[LinkedResourceData, ResourceId]) -> Certificate:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/read_and_download_certificate_information
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        response = self.client.session.get(f'{self.client.API_URL}/certificates/{resource_id}').json()
        return Certificate(response['data'])

    def revoke(self, resource: Union[LinkedResourceData, ResourceId]) -> None:
        """
        https://developer.apple.com/documentation/appstoreconnectapi/revoke_a_certificate
        """
        if isinstance(resource, LinkedResourceData):
            resource_id = resource.id
        else:
            resource_id = resource
        self.client.session.delete(f'{self.client.API_URL}/certificates/{resource_id}')
