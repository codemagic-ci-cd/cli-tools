from __future__ import annotations

import time
from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import cast

from codemagic import cli
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BundleIdArgument
from ..arguments import CertificateArgument
from ..arguments import CommonArgument
from ..arguments import ProfileArgument
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager


class ProfilesActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "create",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        CertificateArgument.CERTIFICATE_RESOURCE_IDS,
        ProfileArgument.DEVICE_RESOURCE_IDS,
        ProfileArgument.PROFILE_TYPE,
        ProfileArgument.PROFILE_NAME,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.PROFILES,
        deprecation_info=cli.ActionDeprecationInfo("create-profile", "0.49.0"),
    )
    def create_profile(
        self,
        bundle_id_resource_id: ResourceId,
        certificate_resource_ids: Sequence[ResourceId],
        device_resource_ids: Optional[Sequence[ResourceId]] = None,
        profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
        profile_name: Optional[str] = None,
        save: bool = False,
        should_print: bool = True,
    ) -> Profile:
        """
        Create provisioning profile of given type
        """

        bundle_id = self.get_bundle_id(bundle_id_resource_id, should_print=False)
        if profile_name:
            name = profile_name
        elif profile_name is None:
            name = f"{bundle_id.attributes.name} {profile_type.value.lower()} {int(time.time())}"
        else:
            raise AppStoreConnectError(f'"{profile_name}" is not a valid {Profile} name')

        create_params = dict(
            name=name,
            profile_type=profile_type,
            bundle_id=bundle_id_resource_id,
            certificates=certificate_resource_ids,
            devices=[],
            omit_keys=["devices"],
        )
        if profile_type.devices_required():
            create_params["devices"] = list(device_resource_ids) if device_resource_ids else []

        try:
            profile = self._create_resource(
                cast("CreatingResourceManager[Profile]", self.api_client.profiles),
                should_print,
                **create_params,
            )
        except ValueError as ve:
            raise AppStoreConnectError(str(ve)) from ve

        if save:
            self._save_profile(profile)
        return profile

    @cli.action(
        "get",
        ProfileArgument.PROFILE_RESOURCE_ID,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.PROFILES,
        deprecation_info=cli.ActionDeprecationInfo("get-profile", "0.49.0"),
    )
    def get_profile(
        self,
        profile_resource_id: ResourceId,
        save: bool = False,
        should_print: bool = True,
    ) -> Profile:
        """
        Get specified Profile from Apple Developer portal
        """

        profile = self._get_resource(profile_resource_id, self.api_client.profiles, should_print)
        if save:
            self._save_profile(profile)
        return profile

    @cli.action(
        "delete",
        ProfileArgument.PROFILE_RESOURCE_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.PROFILES,
        deprecation_info=cli.ActionDeprecationInfo("delete-profile", "0.49.0"),
    )
    def delete_profile(
        self,
        profile_resource_id: ResourceId,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete specified Profile from Apple Developer portal
        """

        self._delete_resource(self.api_client.profiles, profile_resource_id, ignore_not_found)

    @cli.action(
        "list",
        ProfileArgument.PROFILE_TYPE_OPTIONAL,
        ProfileArgument.PROFILE_STATE_OPTIONAL,
        ProfileArgument.PROFILE_NAME,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.PROFILES,
        deprecation_info=cli.ActionDeprecationInfo("list-profiles", "0.49.0"),
    )
    def list_profiles(
        self,
        profile_type: Optional[ProfileType] = None,
        profile_state: Optional[ProfileState] = None,
        profile_name: Optional[str] = None,
        save: bool = False,
        should_print: bool = True,
    ) -> List[Profile]:
        """
        List Profiles from Apple Developer portal matching given constraints
        """
        profile_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name,
        )
        profiles = self._list_resources(
            profile_filter,
            cast("ListingResourceManager[Profile]", self.api_client.profiles),
            should_print,
        )

        if save:
            self._save_profiles(profiles)
        return profiles
