from __future__ import annotations

from abc import ABCMeta
from typing import List
from typing import Optional
from typing import Sequence

from codemagic import cli
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BundleIdArgument
from ..arguments import CommonArgument
from ..arguments import ProfileArgument


class BundleIdsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "create",
        BundleIdArgument.BUNDLE_ID_IDENTIFIER,
        BundleIdArgument.BUNDLE_ID_NAME,
        BundleIdArgument.PLATFORM,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
        deprecation_info=cli.ActionDeprecationInfo("create-bundle-id", "0.49.0"),
    )
    def create_bundle_id(
        self,
        bundle_id_identifier: str,
        bundle_id_name: Optional[str] = None,
        platform: BundleIdPlatform = BundleIdPlatform.IOS,
        should_print: bool = True,
    ) -> BundleId:
        """
        Create Bundle ID in Apple Developer portal for specifier identifier
        """

        if bundle_id_name is None:
            bundle_id_name = bundle_id_identifier.replace(".", " ")

        create_params = dict(identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        return self._create_resource(self.api_client.bundle_ids, should_print, **create_params)

    @cli.action(
        "get",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
        deprecation_info=cli.ActionDeprecationInfo("get-bundle-id", "0.49.0"),
    )
    def get_bundle_id(
        self,
        bundle_id_resource_id: ResourceId,
        should_print: bool = True,
    ) -> BundleId:
        """
        Get specified Bundle ID from Apple Developer portal
        """

        return self._get_resource(bundle_id_resource_id, self.api_client.bundle_ids, should_print)

    @cli.action(
        "list",
        BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
        BundleIdArgument.BUNDLE_ID_NAME,
        BundleIdArgument.PLATFORM_OPTIONAL,
        BundleIdArgument.IDENTIFIER_STRICT_MATCH,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
        deprecation_info=cli.ActionDeprecationInfo("list-bundle-ids", "0.49.0"),
    )
    def list_bundle_ids(
        self,
        bundle_id_identifier: Optional[str] = None,
        bundle_id_name: Optional[str] = None,
        platform: Optional[BundleIdPlatform] = None,
        bundle_id_identifier_strict_match: bool = False,
        should_print: bool = True,
    ) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints
        """

        def predicate(bundle_id):
            return bundle_id.attributes.identifier == bundle_id_identifier

        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=bundle_id_identifier,
            name=bundle_id_name,
            platform=platform,
        )
        bundle_ids = self._list_resources(
            bundle_id_filter,
            self.api_client.bundle_ids,
            should_print,
            filter_predicate=predicate if bundle_id_identifier_strict_match else None,
        )

        return bundle_ids

    @cli.action(
        "delete",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
        deprecation_info=cli.ActionDeprecationInfo("delete-bundle-id", "0.49.0"),
    )
    def delete_bundle_id(
        self,
        bundle_id_resource_id: ResourceId,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete specified Bundle ID from Apple Developer portal
        """

        self._delete_resource(self.api_client.bundle_ids, bundle_id_resource_id, ignore_not_found)

    @cli.action(
        "profiles",
        BundleIdArgument.BUNDLE_ID_RESOURCE_IDS,
        ProfileArgument.PROFILE_TYPE_OPTIONAL,
        ProfileArgument.PROFILE_STATE_OPTIONAL,
        ProfileArgument.PROFILE_NAME,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
        deprecation_info=cli.ActionDeprecationInfo("list-bundle-id-profiles", "0.49.0"),
    )
    def list_bundle_id_profiles(
        self,
        bundle_id_resource_ids: Sequence[ResourceId],
        profile_type: Optional[ProfileType] = None,
        profile_state: Optional[ProfileState] = None,
        profile_name: Optional[str] = None,
        save: bool = False,
        should_print: bool = True,
    ) -> List[Profile]:
        """
        List provisioning profiles from Apple Developer Portal for specified Bundle IDs
        """

        profiles_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name,
        )

        profiles = []
        for resource_id in set(bundle_id_resource_ids):
            bundle_id_profiles = self._list_related_resources(
                resource_id,
                BundleId,
                Profile,
                self.api_client.bundle_ids.list_profiles,
                profiles_filter,
                should_print,
            )
            profiles.extend(bundle_id_profiles)

        if save:
            self._save_profiles(profiles)
        return profiles
