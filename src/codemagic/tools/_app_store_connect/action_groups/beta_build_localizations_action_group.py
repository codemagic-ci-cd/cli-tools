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

    @cli.action('get',
                BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def get_beta_build_localization(self, localization_id, should_print: bool = True):
        """
        Get beta build localization
        """
        return self._get_resource(localization_id, self.api_client.beta_build_localizations, should_print)

    @cli.action('list',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE_OPTIONAL,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def list_beta_build_localizations(
            self,
            build_id: ResourceId,
            locale: Optional[Locale] = None,
            should_print: bool = True) -> List[BetaBuildLocalization]:
        """
        List beta build localizations
        """
        return self._list_resources(
            BetaBuildLocalizations.Filter(build=build_id, locale=locale),
            self.api_client.beta_build_localizations,
            should_print)

    @cli.action('create',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE,
                BuildArgument.WHATS_NEW,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def create_beta_build_localization(
            self,
            build_id: ResourceId,
            locale: Locale,
            whats_new: Optional[str] = None,
            should_print: bool = True) -> BetaBuildLocalization:
        """
        Create a beta build localization
        """
        return self._create_resource(
            self.api_client.beta_build_localizations,
            should_print,
            build=build_id,
            locale=locale,
            whats_new=whats_new)

    @cli.action('delete',
                BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def delete_beta_build_localization(self, localization_id: ResourceId):
        """
        Delete a beta build localization
        """
        self._delete_resource(
            self.api_client.beta_build_localizations, localization_id, ignore_not_found=False)

    @cli.action('modify',
                BuildArgument.BETA_BUILD_LOCALIZATION_ID_RESOURCE_ID,
                BuildArgument.WHATS_NEW,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def update_beta_build_localization(
            self,
            localization_id: ResourceId,
            whats_new: Optional[str] = None,
            should_print: bool = True) -> BetaBuildLocalization:
        """
        Update a beta build localization
        """
        return self._modify_resource(
            self.api_client.beta_build_localizations,
            localization_id,
            ignore_not_found=False,
            should_print=should_print,
            whats_new=whats_new)
