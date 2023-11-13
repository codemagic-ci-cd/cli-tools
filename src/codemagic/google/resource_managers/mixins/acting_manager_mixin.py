from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Generic
from typing import Type
from typing import TypeVar

from googleapiclient import errors
from googleapiclient.http import HttpRequest
from oauth2client.client import Error as OAuth2ClientError

from codemagic.google.errors import GoogleAuthenticationError
from codemagic.google.errors import GoogleClientError
from codemagic.google.errors import GoogleHttpError

if TYPE_CHECKING:
    from ...resources.resource import Resource

ResourceT = TypeVar("ResourceT", bound="Resource")


class ActingManagerMixin(Generic[ResourceT], ABC):
    _logger: logging.Logger

    @property
    @abstractmethod
    def manager_action(self) -> str:
        ...

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...

    def _execute_request(self, request: HttpRequest) -> Dict[str, Any]:
        self._logger.info(f">>> {request.method} {request.uri} {request.body}")
        try:
            response = request.execute()
        except OAuth2ClientError as e:
            self._logger.exception(f"Failed to {self.manager_action} {self.resource_type.get_label()}")
            raise GoogleAuthenticationError(str(e)) from e
        except errors.HttpError as e:
            self._logger.exception(f"Failed to {self.manager_action} {self.resource_type.get_label()}")
            reason = e.reason  # type: ignore
            raise GoogleHttpError(reason) from e
        except errors.Error as e:
            self._logger.exception(f"Failed to {self.manager_action} {self.resource_type.get_label()}")
            raise GoogleClientError(str(e)) from e
        self._logger.info(f"<<< {response}")
        return response
