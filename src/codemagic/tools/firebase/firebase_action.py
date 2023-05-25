import logging
from abc import ABCMeta
from abc import abstractmethod

from codemagic.firebase.api_client import FirebaseApiClient


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
