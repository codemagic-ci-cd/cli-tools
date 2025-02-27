import contextlib
import logging
import pathlib
from abc import ABCMeta
from abc import abstractmethod
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from codemagic.google import GooglePlayClient
from codemagic.google.resources import ResourcePrinter
from codemagic.google.resources.google_play import AppEdit
from codemagic.google.resources.google_play import DeobfuscationFile
from codemagic.google.resources.google_play import DeobfuscationFileType
from codemagic.google.resources.google_play import ExpansionFile
from codemagic.google.resources.google_play import ExpansionFileType
from codemagic.google.resources.google_play import LocalizedText
from codemagic.google.resources.google_play import Track
from codemagic.tools.google_play.argument_types import ReleaseNotesArgument
from codemagic.tools.google_play.arguments import DeobfuscationsArgument
from codemagic.tools.google_play.arguments import ExpansionFileArgument


class GooglePlayBaseAction(metaclass=ABCMeta):
    client: GooglePlayClient
    logger: logging.Logger
    printer: ResourcePrinter

    # Define signatures for self-reference to other action groups

    @contextlib.contextmanager
    def using_app_edit(self, package_name: str, edit: Optional[AppEdit] = None) -> Generator[AppEdit, None, None]:
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
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> Track:
        from .action_groups import TracksActionGroup

        _ = TracksActionGroup.get_track  # Implementation
        raise NotImplementedError

    @abstractmethod
    def list_tracks(
        self,
        package_name: str,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> List[Track]:
        from .action_groups import TracksActionGroup

        _ = TracksActionGroup.list_tracks  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def upload_deobfuscation_file(
        self,
        package_name: str,
        deobfuscation_file_path: pathlib.Path,
        apk_version_code: int,
        deobfuscation_file_type: DeobfuscationFileType = DeobfuscationsArgument.DEOBFUSCATION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> DeobfuscationFile:
        from .action_groups import DeobfuscationFilesActionGroup

        _ = DeobfuscationFilesActionGroup.upload_deobfuscation_file  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def upload_expansion_file(
        self,
        package_name: str,
        expansion_file_path: pathlib.Path,
        apk_version_code: int,
        expansion_file_type: ExpansionFileType = ExpansionFileArgument.EXPANSION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> ExpansionFile:
        from .action_groups import ExpansionFilesActionGroup

        _ = ExpansionFilesActionGroup.upload_expansion_file  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def reference_expansion_file(
        self,
        package_name: str,
        apk_version_code: int,
        references_apk_version_code: int,
        expansion_file_type: ExpansionFileType = ExpansionFileArgument.EXPANSION_FILE_TYPE.get_default(),
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> ExpansionFile:
        from .action_groups import ExpansionFilesActionGroup

        _ = ExpansionFilesActionGroup.reference_expansion_file  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def set_track_release(
        self,
        package_name: str,
        track_name: str,
        version_codes: List[str],
        release_name: Optional[str] = None,
        in_app_update_priority: Optional[int] = None,
        staged_rollout_fraction: Optional[float] = None,
        submit_as_draft: Optional[bool] = None,
        release_notes: Optional[Union[ReleaseNotesArgument, List[LocalizedText]]] = None,
        changes_not_sent_for_review: Optional[bool] = None,
        edit: Optional[AppEdit] = None,
        should_print: bool = True,
    ) -> Track:
        from .action_groups import TracksActionGroup

        _ = TracksActionGroup.set_track_release  # Implementation
        raise NotImplementedError()
