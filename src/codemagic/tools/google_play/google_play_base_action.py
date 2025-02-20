import contextlib
import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence

from codemagic.google import GooglePlayClient
from codemagic.google.resources import ResourcePrinter
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import Track


class GooglePlayBaseAction(metaclass=ABCMeta):
    client: GooglePlayClient
    logger: logging.Logger
    printer: ResourcePrinter

    # Define signatures for self-reference to other action groups

    @contextlib.contextmanager
    def using_app_edit(self, package_name: str) -> Generator[AppEdit, None, None]:
        from ..google_play import GooglePlay

        _ = GooglePlay.using_app_edit  # Implementation
        raise NotImplementedError()

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None: ...

    # Action signatures in alphabetical order

    @abstractmethod
    def get_latest_build_number(
        self,
        package_name: str,
        tracks: Optional[Sequence[str]] = None,
    ) -> Optional[int]:
        from .actions import GetLatestBuildNumberAction

        _ = GetLatestBuildNumberAction.get_latest_build_number  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def get_track(
        self,
        package_name: str,
        track_name: str,
        should_print: bool = True,
    ) -> Track:
        from .action_groups import TracksActionGroup

        _ = TracksActionGroup.get_track  # Implementation
        raise NotImplementedError

    @abstractmethod
    def list_tracks(
        self,
        package_name: str,
        should_print: bool = True,
    ) -> List[Track]:
        from .action_groups import TracksActionGroup

        _ = TracksActionGroup.list_tracks  # Implementation
        raise NotImplementedError()
