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
    def list_beta_build_localization(
            self, build_id: ResourceId, locale: Optional[Locale]) -> List[BetaBuildLocalization]:
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
            self, build_id: ResourceId, locale: Locale, whats_new: str) -> BetaBuildLocalization:
        """
        Create a beta build localization for given locale
        """
        return self._create_resource(
            self.api_client.beta_build_localizations,
            should_print=True,
            build=build_id,
            locale=locale,
            whats_new=whats_new)

    @cli.action('delete',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def delete_beta_build_localization(self, build_id: ResourceId, locale: Locale):
        """
        Delete a beta build localization for given locale
        """
        localization = next(iter(self._list_resources(
            BetaBuildLocalizations.Filter(build=build_id, locale=locale),
            self.api_client.beta_build_localizations,
            should_print=True,
        )), None)

        if not localization:
            raise cli.CliAppException(f'Could not find {locale} locale for build {build_id}.')

        self._delete_resource(
            self.api_client.beta_build_localizations, localization.id, ignore_not_found=False)

    @cli.action('modify',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.LOCALE,
                BuildArgument.WHATS_NEW,
                action_group=AppStoreConnectActionGroup.BETA_BUILDS_LOCALIZATIONS)
    def update_beta_build_localization(
            self, build_id: ResourceId, locale: Locale, whats_new: str) -> Optional[BetaBuildLocalization]:
        """
        Update a beta build localization for given locale
        """
        localization = next(iter(self._list_resources(
            BetaBuildLocalizations.Filter(build=build_id, locale=locale),
            self.api_client.beta_build_localizations,
            should_print=True,
        )), None)

        if not localization:
            raise cli.CliAppException(f'Could not find {locale} locale for build {build_id}.')

        return self._modify_resource(
            self.api_client.beta_build_localizations, localization.id, ignore_not_found=False, whats_new=whats_new)
