from __future__ import annotations

from abc import ABCMeta
from typing import List
from typing import Optional

from codemagic import cli
from codemagic.apple.app_store_connect.versioning import BetaBuildLocalizations
from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument


class BetaBuildLocalizationsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('list',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE_OPTIONAL,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def list_beta_build_localizations(
            self, build_id: ResourceId, locale: Optional[Locale] = None) -> List[BetaBuildLocalization]:
        """
        List beta build localization
        """
        return self._list_resources(
            BetaBuildLocalizations.Filter(build=build_id, locale=locale),
            self.api_client.beta_build_localizations,
            should_print=True)

    @cli.action('create',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE,
                BuildArgument.WHATS_NEW,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def create_beta_build_localization(
            self, build_id: ResourceId, locale: Locale, whats_new: Optional[str] = None) -> BetaBuildLocalization:
        """
        Create a beta build localization for given locale
        """
        return self._create_resource(
            self.api_client.beta_build_localizations,
            build=build_id,
            locale=locale,
            whats_new=whats_new,
            should_print=True)

    @cli.action('delete',
                BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def delete_beta_build_localization(self, localization_id: ResourceId):
        """
        Delete a beta build localization for given locale
        """
        self._delete_resource(
            self.api_client.beta_build_localizations, localization_id, ignore_not_found=False)

    @cli.action('modify',
                BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
                BuildArgument.WHATS_NEW,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def update_beta_build_localization(
            self, localization_id: ResourceId, whats_new: Optional[str] = None) -> BetaBuildLocalization:
        """
        Update a beta build localization for given locale
        """
        return self._modify_resource(
            self.api_client.beta_build_localizations, localization_id, ignore_not_found=False, whats_new=whats_new)
