from __future__ import annotations

import contextlib
import socket
from abc import ABC
from abc import abstractmethod
from functools import cached_property
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


@contextlib.contextmanager
def _custom_http_timeout(seconds: int):
    current_default = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(seconds)
        yield
    finally:
        socket.setdefaulttimeout(current_default)


class GoogleClient(Generic[GoogleResourceT], ABC):
    def __init__(self, service_account_dict: Dict):
        self._service_account_dict = service_account_dict

    @property
    @abstractmethod
    def google_service_name(self) -> str: ...

    @property
    @abstractmethod
    def google_service_version(self) -> str: ...

    def _build_google_resource(self) -> GoogleResourceT:
        try:
            with _custom_http_timeout(seconds=10 * 60):
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

    @cached_property
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

    @cached_property
    def _credentials(self) -> ServiceAccountCredentials:
        try:
            return ServiceAccountCredentials.from_json_keyfile_dict(self._service_account_dict)
        except KeyError as e:
            raise GoogleCredentialsError(str(e))
