from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import TypeVar

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.service_account import ServiceAccountCredentials

from codemagic.google.errors import GoogleClientError
from codemagic.google.errors import GoogleCredentialsError
from codemagic.google.errors import GoogleHttpError
from codemagic.utilities import log

GoogleResourceT = TypeVar("GoogleResourceT", bound=discovery.Resource)


class GoogleClient(Generic[GoogleResourceT], ABC):
    google_service_version: ClassVar[str] = "v1"

    def __init__(self, service_account_dict: Dict):
        self._service_account_dict = service_account_dict

    @property
    @abstractmethod
    def google_service_name(self) -> str:
        ...

    def _build_google_resource(self) -> GoogleResourceT:
        try:
            return discovery.build(
                self.google_service_name,
                self.google_service_version,
                credentials=self._credentials,
            )
        except Exception:
            log.get_file_logger(self.__class__).exception(
                f"Failed to construct {self.google_service_version} {self.google_service_name} service resource",
            )
            raise

    @property
    def google_resource(self) -> GoogleResourceT:
        try:
            return self._build_google_resource()
        except ValueError as e:
            raise GoogleCredentialsError(str(e))
        except errors.HttpError as e:
            reason = e.reason  # type: ignore
            raise GoogleHttpError(reason)
        except errors.Error as e:
            raise GoogleClientError(str(e))

    @property
    def _credentials(self) -> ServiceAccountCredentials:
        try:
            return ServiceAccountCredentials.from_json_keyfile_dict(self._service_account_dict)
        except KeyError as e:
            raise GoogleCredentialsError(str(e))
