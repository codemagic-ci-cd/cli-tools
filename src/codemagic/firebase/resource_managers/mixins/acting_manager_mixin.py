from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import Type
from typing import TypeVar

from googleapiclient import errors
from googleapiclient.http import HttpRequest
from oauth2client.client import Error as OAuth2ClientError

from ...errors import AuthenticationError
from ...errors import ClientError
from ...errors import FirebaseApiHttpError

if TYPE_CHECKING:
    from ...resources.resource import Resource

ResourceT = TypeVar('ResourceT', bound='Resource')


class ActingManagerMixin(Generic[ResourceT], ABC):
    manager_action: ClassVar[str]

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...

    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        ...

    def _execute_request(self, request: HttpRequest) -> Dict[str, Any]:
        try:
            return request.execute()
        except OAuth2ClientError as e:
            self.logger.exception(f'Failed to {self.manager_action} Firebase {self.resource_type.get_label()}')
            raise AuthenticationError(str(e)) from e
        except errors.HttpError as e:
            self.logger.exception(f'Failed to {self.manager_action} Firebase {self.resource_type.get_label()}')
            reason = e.reason  # type: ignore
            raise FirebaseApiHttpError(reason) from e
        except errors.Error as e:
            self.logger.exception(f'Failed to {self.manager_action} Firebase {self.resource_type.get_label()}')
            raise ClientError(str(e)) from e
