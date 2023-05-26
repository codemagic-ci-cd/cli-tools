import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import List

from codemagic.firebase.api_client import FirebaseApiClient
from codemagic.firebase.resources import Release


class FirebaseAction(metaclass=ABCMeta):
    api_client: FirebaseApiClient
    logger: logging.Logger

    # Define signatures for self-reference to other action groups

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None:
        ...

    # Action signatures in alphabetical order

    @abstractmethod
    def get_latest_build_version(
        self,
        project_id: str,
        app_id: str,
    ) -> int:
        from .actions import GetLatestBuildVersionAction
        _ = GetLatestBuildVersionAction.get_latest_build_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_releases(
        self,
        project_id: str,
        app_id: str,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        from .action_groups.releases_action_group import ReleasesActionGroup
        _ = ReleasesActionGroup.list_releases  # Implementation
        raise NotImplementedError()
