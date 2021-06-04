from __future__ import annotations

from abc import ABCMeta

from codemagic import cli
from codemagic.apple.resources import BetaBuildLocalization
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument


class BetaBuildLocalizationsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('create',
                BuildArgument.BUILD_ID_RESOURCE_ID_OPTIONAL,
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
