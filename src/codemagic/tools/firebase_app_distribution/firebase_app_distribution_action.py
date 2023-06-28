import logging
from abc import ABC
from abc import abstractmethod
from typing import List

from codemagic.google.firebase_client import FirebaseClient
from codemagic.google.resources import OrderBy
from codemagic.google.resources import Release


class FirebaseAppDistributionAction(ABC):
    client: FirebaseClient
    logger: logging.Logger

    # Define signatures for self-reference to other action groups

    @property
    @abstractmethod
    def project_id(self):
        ...

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None:
        ...

    # Action signatures in alphabetical order

    @abstractmethod
    def get_latest_build_version(self, app_id: str, should_print: bool = True) -> int:
        from .actions import GetLatestBuildVersionAction

        _ = GetLatestBuildVersionAction.get_latest_build_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_releases(
        self,
        app_id: str,
        limit: int = 25,
        order_by: OrderBy = OrderBy.CREATE_TIME_DESC,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        from .action_groups.releases_action_group import ReleasesActionGroup

        _ = ReleasesActionGroup.list_releases  # Implementation
        raise NotImplementedError()
