from abc import ABC
from abc import abstractmethod
from typing import Union

from googleapiclient import errors


class GooglePlayDeveloperAPIClientError(Exception):
    @classmethod
    def _get_error_reason(cls, error: Union[errors.Error, errors.HttpError]) -> str:
        if isinstance(error, errors.Error):
            return str(error)
        else:
            reason = error._get_reason()
            return reason or 'Http Error'


class AuthorizationError(GooglePlayDeveloperAPIClientError):
    def __init__(self, error: Union[errors.Error, errors.HttpError]):
        reason = self._get_error_reason(error)
        super().__init__(f'Unable to authorize with provided credentials. {reason}')


class EditError(GooglePlayDeveloperAPIClientError):
    def __init__(self, action: str, package_name: str, error: Union[errors.Error, errors.HttpError]):
        reason = self._get_error_reason(error)
        super().__init__(f'Unable to {action} an edit for package "{package_name}". {reason}')


class _RequestError(GooglePlayDeveloperAPIClientError, ABC):
    def __init__(
            self,
            resource_description: str,
            package_name: str,
            request_error: Union[errors.Error, errors.HttpError],
    ):
        self.package_name = package_name
        self.request_error = request_error
        super().__init__(self._get_message(resource_description))

    def _get_reason(self) -> str:
        return self._get_error_reason(self.request_error)

    @abstractmethod
    def _get_message(self, resource_description: str) -> str:
        raise NotImplementedError()


class GetResourceError(_RequestError):
    def _get_message(self, resource_description: str) -> str:
        return (
            f'Failed to get {resource_description} from Google Play for package "{self.package_name}". '
            f'{self._get_reason()}'
        )


class ListResourcesError(_RequestError):
    def _get_message(self, resource_description: str) -> str:
        return (
            f'Failed to list {resource_description} from Google Play for package "{self.package_name}". '
            f'{self._get_reason()}'
        )
