from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Generic
from typing import Literal
from typing import Type
from typing import TypeVar

from googleapiclient import discovery
from googleapiclient import errors
from googleapiclient.http import HttpRequest
from oauth2client.client import Error as OAuth2ClientError

from codemagic.google.errors import GoogleAuthenticationError
from codemagic.google.errors import GoogleClientError
from codemagic.google.errors import GoogleHttpError
from codemagic.utilities import log

from ..resources import Resource

ResourceT = TypeVar("ResourceT", bound=Resource)
GoogleServiceT = TypeVar("GoogleServiceT", bound=discovery.Resource)


class ResourceManager(Generic[ResourceT, GoogleServiceT], ABC):
    def __init__(self, google_service: GoogleServiceT):
        self._google_service = google_service
        self._logger = log.get_file_logger(self.__class__)

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        raise NotImplementedError()

    def _execute_request(
        self,
        request: HttpRequest,
        request_type: Literal["insert", "get", "list", "update", "delete"],
    ) -> Dict[str, Any]:
        self._logger.info(f">>> {request.method} {request.uri} {request.body}")
        try:
            response = request.execute()
        except OAuth2ClientError as e:
            self._logger.exception(f"Failed to {request_type} {self.resource_type.__name__}")
            raise GoogleAuthenticationError(str(e)) from e
        except errors.HttpError as e:
            self._logger.exception(f"Failed to {request_type} {self.resource_type.__name__}")
            reason = e.reason  # type: ignore
            raise GoogleHttpError(reason) from e
        except errors.Error as e:
            self._logger.exception(f"Failed to {request_type} {self.resource_type.__name__}")
            raise GoogleClientError(str(e)) from e
        self._logger.info(f"<<< {response}")
        return response
