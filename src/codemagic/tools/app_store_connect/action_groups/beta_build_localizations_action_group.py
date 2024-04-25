from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect.versioning import BetaBuildLocalizations
from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument
from ..arguments import CommonArgument
from ..arguments import Types

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ModifyingResourceManager


class BetaBuildLocalizationsActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "get",
        BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
        action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS,
    )
    def get_beta_build_localization(
        self,
        localization_id: ResourceId,
        should_print: bool = True,
    ) -> BetaBuildLocalization:
        """
        Get beta build localization
        """
        return self._get_resource(localization_id, self.api_client.beta_build_localizations, should_print)

    @cli.action(
        "list",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        BuildArgument.LOCALE_OPTIONAL,
        action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS,
    )
    def list_beta_build_localizations(
        self,
        build_id: ResourceId,
        locale: Optional[Locale] = None,
        should_print: bool = True,
    ) -> List[BetaBuildLocalization]:
        """
        List beta build localizations
        """
        return self._list_resources(
            BetaBuildLocalizations.Filter(build=build_id, locale=locale),
            cast("ListingResourceManager[BetaBuildLocalization]", self.api_client.beta_build_localizations),
            should_print,
        )

    @cli.action(
        "create",
        BuildArgument.BUILD_ID_RESOURCE_ID,
        BuildArgument.LOCALE_DEFAULT,
        BuildArgument.WHATS_NEW,
        action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS,
    )
    def create_beta_build_localization(
        self,
        build_id: ResourceId,
        locale: Optional[Locale] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> BetaBuildLocalization:
        """
        Create a beta build localization if it doesn't exist or update existing
        beta build localization for specified locale
        """
        if locale is None:
            app = self.api_client.builds.read_app(build_id)
            locale = app.attributes.primaryLocale
            msg_template = "Using application %s primary locale %s for beta build localization"
            self.logger.info(msg_template, app.attributes.name, locale.value)

        beta_localizations_filter = BetaBuildLocalizations.Filter(build=build_id, locale=locale)
        try:
            beta_build_localizations = self.api_client.beta_build_localizations.list(beta_localizations_filter)
        except AppStoreConnectApiError:
            beta_build_localizations = []

        # The notes are automatically created for default locale some time after the build is
        # submitted to App Store Connect. In that case we just need to modify the resource.
        # Otherwise, either when the resource is not created yet, or we are working with non-default
        # locales, we need to create the BetaBuildLocalization resource by ourselves.
        if not beta_build_localizations:
            return self._create_resource(
                cast("CreatingResourceManager[BetaBuildLocalization]", self.api_client.beta_build_localizations),
                should_print,
                build=build_id,
                locale=locale,
                whats_new=self._get_whats_new_value(whats_new),
            )
        else:
            beta_build_localization = beta_build_localizations[0]
            return self.update_beta_build_localization(beta_build_localization.id, whats_new)

    @cli.action(
        "delete",
        BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS,
    )
    def delete_beta_build_localization(self, localization_id: ResourceId, ignore_not_found: bool = False):
        """
        Delete a beta build localization
        """
        self._delete_resource(self.api_client.beta_build_localizations, localization_id, ignore_not_found)

    @cli.action(
        "modify",
        BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
        BuildArgument.WHATS_NEW,
        action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS,
    )
    def update_beta_build_localization(
        self,
        localization_id: ResourceId,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> BetaBuildLocalization:
        """
        Update a beta build localization
        """
        return self._modify_resource(
            cast("ModifyingResourceManager[BetaBuildLocalization]", self.api_client.beta_build_localizations),
            localization_id,
            should_print,
            whats_new=self._get_whats_new_value(whats_new),
        )

    @classmethod
    def _get_whats_new_value(cls, whats_new: Optional[Union[str, Types.WhatsNewArgument]]) -> Optional[str]:
        if whats_new is None:
            return None
        elif isinstance(whats_new, str):
            return whats_new
        elif isinstance(whats_new, Types.WhatsNewArgument):
            return whats_new.value
        raise TypeError(f"Invalid type {type(whats_new)} for whats_new")
