import pathlib
from unittest import mock

from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.tools import AppStoreConnect
from codemagic.tools.app_store_connect.arguments import AppStoreVersionLocalizationInfo
from codemagic.tools.app_store_connect.arguments import Types


def test_app_store_submission():
    app_store_connect = AppStoreConnect(
        issuer_id=IssuerId("issuer-id"),
        key_identifier=KeyIdentifier("key-identifier"),
        private_key="private-key",
    )
    mock_ipa = mock.MagicMock(version="1.2.3", is_for_tvos=lambda: False)
    mock_build = mock.MagicMock(id="mock-build-id")

    with mock.patch.object(
        app_store_connect,
        "_get_publishing_application_packages",
        return_value=[mock_ipa],
    ), mock.patch.object(
        app_store_connect,
        "_publish_application_package",
    ), mock.patch.object(
        app_store_connect,
        "_get_uploaded_build_application",
        return_value=mock.MagicMock(),
    ), mock.patch.object(
        app_store_connect,
        "_get_uploaded_build",
        return_value=mock_build,
    ), mock.patch.object(
        app_store_connect,
        "wait_until_build_is_processed",
    ), mock.patch.object(
        app_store_connect,
        "submit_to_app_store",
    ) as mock_submit_to_app_store:
        app_store_connect.publish(
            [pathlib.Path("path/to/application.ipa")],
            submit_to_app_store=True,
            release_type=ReleaseType.MANUAL,
            app_store_version_localizations=Types.AppStoreVersionLocalizationInfoArgument(
                raw_value='[{"locale":"en-GB", "whats_new":"U.K. notes"}, {"locale":"fi","whats_new":"Finnish notes"}]',
            ),
        )

    mock_submit_to_app_store.assert_called_once_with(
        "mock-build-id",
        max_build_processing_wait=0,
        app_store_version_info=None,
        app_store_version_localizations=[
            AppStoreVersionLocalizationInfo(locale=Locale.EN_GB, whats_new="U.K. notes"),
            AppStoreVersionLocalizationInfo(locale=Locale.FI, whats_new="Finnish notes"),
        ],
        cancel_previous_submissions=False,
        copyright=None,
        description=None,
        disable_phased_release=None,
        earliest_release_date=None,
        enable_phased_release=None,
        keywords=None,
        locale=None,
        marketing_url=None,
        platform=Platform.IOS,
        promotional_text=None,
        release_type=ReleaseType.MANUAL,
        support_url=None,
        version_string="1.2.3",
        whats_new=None,
    )
