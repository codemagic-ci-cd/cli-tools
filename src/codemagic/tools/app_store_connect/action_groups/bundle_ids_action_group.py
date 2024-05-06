from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdCapability
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CapabilityType
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BundleIdArgument
from ..arguments import CommonArgument
from ..arguments import ProfileArgument
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager


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
        return self._create_resource(
            cast("CreatingResourceManager[BundleId]", self.api_client.bundle_ids),
            should_print,
            **create_params,
        )

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
            cast("ListingResourceManager[BundleId]", self.api_client.bundle_ids),
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

    @cli.action(
        "capabilities",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
    )
    def list_bundle_id_capabilities(
        self,
        bundle_id_resource_id: ResourceId,
        should_print: bool = True,
    ) -> List[BundleIdCapability]:
        """
        Check the capabilities that are enabled for identifier
        """
        return self._list_related_resources(
            bundle_id_resource_id,
            BundleId,
            BundleIdCapability,
            self.api_client.bundle_ids.list_capabilities,
            None,
            should_print,
        )

    @cli.action(
        "enable-capabilities",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        BundleIdArgument.CAPABILITY_TYPES,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
    )
    def enable_bundle_id_capabilities(
        self,
        bundle_id_resource_id: ResourceId,
        capabilities: Sequence[Union[CapabilityType, str]],
    ):
        """
        Enable capabilities for identifier
        """
        capability_types = self._resolve_capability_types(capabilities)
        bundle_id = self._get_bundle_id(bundle_id_resource_id)
        self.logger.info(Colors.BLUE(f'Enable {BundleIdCapability.s} for identifier "{bundle_id.attributes.name}"'))

        for capability_type in capability_types:
            self._enable_capability(bundle_id, capability_type)

        success_message = f'Successfully enabled {BundleIdCapability.s} for identifier "{bundle_id.attributes.name}"'
        self.logger.info(Colors.GREEN(success_message))

    @cli.action(
        "disable-capabilities",
        BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
        BundleIdArgument.CAPABILITY_TYPES,
        action_group=AppStoreConnectActionGroup.BUNDLE_IDS,
    )
    def disable_bundle_id_capabilities(
        self,
        bundle_id_resource_id: ResourceId,
        capabilities: Sequence[Union[CapabilityType, str]],
    ):
        """
        Disable identifier capabilities
        """
        capability_types = self._resolve_capability_types(capabilities)
        bundle_id = self._get_bundle_id(bundle_id_resource_id)
        self.logger.info(Colors.BLUE(f'Disable {BundleIdCapability.s} for identifier "{bundle_id.attributes.name}"'))

        enabled_capabilities = self._get_capabilities(bundle_id, capability_types)
        if not enabled_capabilities:
            skip_message = (
                f"None of the specified {BundleIdCapability.s} are enabled for identifier "
                f'"{bundle_id.attributes.name}". Skip disabling.'
            )
            self.logger.info(Colors.YELLOW(skip_message))
            return

        for capability in enabled_capabilities:
            self._disable_capability(bundle_id, capability)

        success_message = f'Successfully disabled {BundleIdCapability.s} for identifier "{bundle_id.attributes.name}"'
        self.logger.info(Colors.GREEN(success_message))

    def _get_bundle_id(self, bundle_id_resource_id: ResourceId) -> BundleId:
        try:
            return self.api_client.bundle_ids.read(bundle_id_resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error

    @classmethod
    def _resolve_capability_types(
        cls,
        capabilities: Optional[Sequence[Union[CapabilityType, str]]],
    ) -> List[CapabilityType]:
        if not capabilities:
            return []
        return [c if isinstance(c, CapabilityType) else CapabilityType.from_display_name(c) for c in capabilities]

    def _get_capabilities(
        self,
        bundle_id: BundleId,
        capability_types: Sequence[CapabilityType],
    ) -> List[BundleIdCapability]:
        try:
            capabilities = self.api_client.bundle_ids.list_capabilities(bundle_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                str(api_error),
                api_error_response=api_error.error_response,
            ) from api_error
        return [c for c in capabilities if c.attributes.capabilityType in capability_types]

    def _enable_capability(self, bundle_id: BundleId, capability_type: CapabilityType) -> BundleIdCapability:
        try:
            capability = self.api_client.bundle_id_capabilities.enable(
                capability_type,
                bundle_id=bundle_id.id,
            )
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                (
                    f"Failed to enable capability {capability_type.value} for bundle identifier "
                    f'"{bundle_id.attributes.name}" ({bundle_id.id}): {api_error}'
                ),
                api_error_response=api_error.error_response,
            ) from api_error

        self.echo(Colors.BLUE(f"-- Enabled {capability.__class__} --"))
        self.echo(f"{capability}")
        return capability

    def _disable_capability(self, bundle_id: BundleId, capability: BundleIdCapability):
        try:
            self.api_client.bundle_id_capabilities.disable(capability)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(
                (
                    f"Failed to disable capability {capability.attributes.capabilityType.value} "
                    f"for bundle identifier "
                    f'"{bundle_id.attributes.name}" ({bundle_id.id}): {api_error}'
                ),
                api_error_response=api_error.error_response,
            ) from api_error

        self.echo(Colors.BLUE(f"-- Disabled {capability.__class__} --"))
        self.echo(f"{capability}")
