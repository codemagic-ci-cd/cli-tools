from __future__ import annotations

from abc import ABCMeta
from typing import Optional
from typing import Union

from codemagic import cli
from codemagic.apple.resources import AppStoreVersionLocalization
from codemagic.apple.resources import Locale
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import AppStoreVersionArgument
from ..arguments import AppStoreVersionLocalizationArgument
from ..arguments import CommonArgument
from ..arguments import Types


class AppStoreVersionLocalizationsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action(
        'get',
        AppStoreVersionLocalizationArgument.APP_STORE_VERSION_LOCALIZATION_ID,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_LOCALIZATIONS,
    )
    def get_app_store_version_localization(
        self,
        app_store_version_localization_id: ResourceId,
        should_print: bool = True,
    ) -> AppStoreVersionLocalization:
        """
        Read App Store Version Localization Information.
        Get localized version-level information.
        """
        return self._get_resource(
            app_store_version_localization_id,
            self.api_client.app_store_version_localizations,
            should_print,
        )

    @cli.action(
        'create',
        AppStoreVersionArgument.APP_STORE_VERSION_ID,
        AppStoreVersionLocalizationArgument.LOCALE,
        AppStoreVersionLocalizationArgument.DESCRIPTION,
        AppStoreVersionLocalizationArgument.KEYWORDS,
        AppStoreVersionLocalizationArgument.MARKETING_URL,
        AppStoreVersionLocalizationArgument.PROMOTIONAL_TEXT,
        AppStoreVersionLocalizationArgument.SUPPORT_URL,
        AppStoreVersionLocalizationArgument.WHATS_NEW,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_LOCALIZATIONS,
    )
    def create_app_store_version_localization(
        self,
        app_store_version_id: ResourceId,
        locale: Locale,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> AppStoreVersionLocalization:
        """
        Create an App Store Version Localization.
        Add localized version-level information for a new locale.
        """
        create_params = dict(
            app_store_version=app_store_version_id,
            locale=locale,
            description=description,
            keywords=keywords,
            marketing_url=marketing_url,
            promotional_text=promotional_text,
            support_url=support_url,
            whats_new=whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new,
        )
        return self._create_resource(
            self.api_client.app_store_version_localizations,
            should_print,
            **{k: v for k, v in create_params.items() if v is not None},
        )

    @cli.action(
        'modify',
        AppStoreVersionLocalizationArgument.APP_STORE_VERSION_LOCALIZATION_ID,
        AppStoreVersionLocalizationArgument.DESCRIPTION,
        AppStoreVersionLocalizationArgument.KEYWORDS,
        AppStoreVersionLocalizationArgument.MARKETING_URL,
        AppStoreVersionLocalizationArgument.PROMOTIONAL_TEXT,
        AppStoreVersionLocalizationArgument.SUPPORT_URL,
        AppStoreVersionLocalizationArgument.WHATS_NEW,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_LOCALIZATIONS,
    )
    def update_app_store_version_localization(
        self,
        app_store_version_localization_id: ResourceId,
        description: Optional[str] = None,
        keywords: Optional[str] = None,
        marketing_url: Optional[str] = None,
        promotional_text: Optional[str] = None,
        support_url: Optional[str] = None,
        whats_new: Optional[Union[str, Types.WhatsNewArgument]] = None,
        should_print: bool = True,
    ) -> AppStoreVersionLocalization:
        """
        Modify an App Store Version Localization.
        Edit localized version-level information for a particular language.
        """
        return self._modify_resource(
            self.api_client.app_store_version_localizations,
            app_store_version_localization_id,
            should_print,
            description=description,
            keywords=keywords,
            marketing_url=marketing_url,
            promotional_text=promotional_text,
            support_url=support_url,
            whats_new=whats_new.value if isinstance(whats_new, Types.WhatsNewArgument) else whats_new,
        )

    @cli.action(
        'delete',
        AppStoreVersionLocalizationArgument.APP_STORE_VERSION_LOCALIZATION_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_LOCALIZATIONS,
    )
    def delete_app_store_version_localization(
        self,
        app_store_version_localization_id: ResourceId,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete an App Store Version Localization.
        Remove a language from your version metadata.
        """
        self._delete_resource(
            self.api_client.app_store_version_localizations,
            app_store_version_localization_id,
            ignore_not_found,
        )
