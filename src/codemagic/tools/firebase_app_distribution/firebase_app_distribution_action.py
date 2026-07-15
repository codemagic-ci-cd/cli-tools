import logging
from abc import ABC
from abc import abstractmethod
from typing import List

from codemagic.google.firebase_client import FirebaseClient
from codemagic.google.resources import ResourcePrinter
from codemagic.google.resources.firebase import Release

from .argument_types import ReleasesOrderByArgument


class FirebaseAppDistributionAction(ABC):
    client: FirebaseClient
    logger: logging.Logger
    printer: ResourcePrinter

    # Define signatures for self-reference to other action groups

    @property
    @abstractmethod
    def project_number(self): ...

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None: ...

    # Action signatures in alphabetical order

    @abstractmethod
    def get_latest_build_version(self, app_id: str, should_print: bool = True) -> str:
        from .actions import GetLatestBuildVersionAction

        _ = GetLatestBuildVersionAction.get_latest_build_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_releases(
        self,
        app_id: str,
        limit: int = 25,
        order_by: ReleasesOrderByArgument = ReleasesOrderByArgument.CREATE_TIME_DESC,
        should_print: bool = True,
    ) -> List[Release]:
        from .action_groups.releases_action_group import ReleasesActionGroup

        _ = ReleasesActionGroup.list_releases  # Implementation
        raise NotImplementedError()
