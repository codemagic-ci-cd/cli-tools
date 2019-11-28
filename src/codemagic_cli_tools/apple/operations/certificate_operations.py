from typing import List
from typing import Optional
from typing import Union

from apple.resources import Certificate
from apple.resources import CertificateType
from apple.resources import LinkedResourceData
from apple.resources import ResourceId
from .base_operations import BaseOperations
from .base_operations import BaseOrdering


class CertificateOrdering(BaseOrdering):
    CERTIFICATE_TYPE = 'certificateType'
    DISPLAY_NAME = 'displayName'
    ID = 'id'
    SERIAL_NUMBER = 'serialNumber'


class CertificateOperations(BaseOperations):
    """
    Certificate operations
    https://developer.apple.com/documentation/appstoreconnectapi/certificates
    """

    def create(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/create_a_certificate
        """
        raise NotImplemented  # TODO

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

    def revoke(self):
        """
        https://developer.apple.com/documentation/appstoreconnectapi/revoke_a_certificate
        """
        raise NotImplemented  # TODO
