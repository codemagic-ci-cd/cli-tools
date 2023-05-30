from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Dict
from typing import cast

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.service_account import ServiceAccountCredentials

from .errors import ClientError
from .errors import CredentialsError
from .errors import FirebaseApiHttpError
from .resource_managers.release_manager import ReleaseManager

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource


class FirebaseClient:
    def __init__(self, service_account_dict: Dict):
        self._service_account_dict = service_account_dict

    @property
    def _credentials(self) -> ServiceAccountCredentials:
        try:
            return ServiceAccountCredentials.from_json_keyfile_dict(self._service_account_dict)
        except KeyError as e:
            raise CredentialsError(str(e))

    @property
    def _firebase_app_distribution(self) -> FirebaseAppDistributionResource:
        try:
            recourse = discovery.build('firebaseappdistribution', 'v1', credentials=self._credentials)
        except ValueError as e:
            raise CredentialsError(str(e))
        except errors.HttpError as e:
            reason = e.reason  # type: ignore
            raise FirebaseApiHttpError(reason)
        except errors.Error as e:
            raise ClientError(str(e))
        else:
            return cast('FirebaseAppDistributionResource', recourse)

    @property
    def releases(self) -> ReleaseManager:
        return ReleaseManager(self._firebase_app_distribution)
