from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import TypeVar
from typing import cast

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.service_account import ServiceAccountCredentials

from codemagic.google.errors import GoogleClientError
from codemagic.google.errors import GoogleCredentialsError
from codemagic.google.errors import GoogleHttpError

ServiceResourceT = TypeVar('ServiceResourceT', bound=discovery.Resource)


class GoogleClient(Generic[ServiceResourceT], ABC):
    service_version: ClassVar[str] = 'v1'

    def __init__(self, service_account_dict: Dict):
        self._service_account_dict = service_account_dict

    @property
    @abstractmethod
    def service_name(self) -> str:
        ...

    @property
    def service_resource(self) -> ServiceResourceT:
        try:
            recourse = discovery.build(self.service_name, self.service_version, credentials=self._credentials)
        except ValueError as e:
            raise GoogleCredentialsError(str(e))
        except errors.HttpError as e:
            reason = e.reason  # type: ignore
            raise GoogleHttpError(reason)
        except errors.Error as e:
            raise GoogleClientError(str(e))
        else:
            return cast(ServiceResourceT, recourse)

    @property
    def _credentials(self) -> ServiceAccountCredentials:
        try:
            return ServiceAccountCredentials.from_json_keyfile_dict(self._service_account_dict)
        except KeyError as e:
            raise GoogleCredentialsError(str(e))
