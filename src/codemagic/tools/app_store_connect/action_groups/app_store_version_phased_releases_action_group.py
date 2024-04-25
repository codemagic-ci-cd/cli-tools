from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import Optional
from typing import cast

from codemagic import cli
from codemagic.apple.resources import AppStoreVersionPhasedRelease
from codemagic.apple.resources import PhasedReleaseState
from codemagic.apple.resources import ResourceReference

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import AppStoreVersionPhasedReleaseArgument
from ..arguments import CommonArgument

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ModifyingResourceManager


class AppStoreVersionPhasedReleasesActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "enable",
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        AppStoreVersionPhasedReleaseArgument.PHASED_RELEASE_STATE_OPTIONAL,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_PHASED_RELEASES,
    )
    def enable_app_store_version_phased_release(
        self,
        app_store_version_id: ResourceReference,
        *,
        phased_release_state: Optional[PhasedReleaseState] = None,
        should_print: bool = True,
    ) -> AppStoreVersionPhasedRelease:
        """
        Enable phased release for an App Store version
        """

        return self._create_resource(
            cast(
                "CreatingResourceManager[AppStoreVersionPhasedRelease]",
                self.api_client.app_store_version_phased_releases,
            ),
            should_print,
            app_store_version=app_store_version_id,
            **({"phased_release_state": phased_release_state} if phased_release_state else {}),
        )

    @cli.action(
        "set-state",
        AppStoreVersionPhasedReleaseArgument.APP_STORE_VERSION_PHASED_RELEASE_ID,
        AppStoreVersionPhasedReleaseArgument.PHASED_RELEASE_STATE,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_PHASED_RELEASES,
    )
    def set_app_store_version_phased_release_state(
        self,
        app_store_version_phased_release: ResourceReference,
        *,
        phased_release_state: PhasedReleaseState,
        should_print: bool = True,
    ) -> AppStoreVersionPhasedRelease:
        """
        Pause or resume an App Store version phased release, or immediately release an app
        """
        return self._modify_resource(
            cast(
                "ModifyingResourceManager[AppStoreVersionPhasedRelease]",
                self.api_client.app_store_version_phased_releases,
            ),
            app_store_version_phased_release,
            should_print,
            phased_release_state=phased_release_state,
        )

    @cli.action(
        "cancel",
        AppStoreVersionPhasedReleaseArgument.APP_STORE_VERSION_PHASED_RELEASE_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_PHASED_RELEASES,
    )
    def cancel_app_store_version_phased_release(
        self,
        app_store_version_phased_release: ResourceReference,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Cancel a planned App Store version phased release that has not been started
        """
        self._delete_resource(
            self.api_client.app_store_version_phased_releases,
            app_store_version_phased_release,
            ignore_not_found,
        )
