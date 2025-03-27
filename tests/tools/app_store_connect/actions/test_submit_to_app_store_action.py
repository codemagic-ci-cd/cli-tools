from unittest import mock

from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreVersion
from codemagic.apple.resources import Build
from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ReleaseType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import ReviewSubmission
from codemagic.apple.resources import ReviewSubmissionItem
from codemagic.tools import AppStoreConnect
from codemagic.tools.app_store_connect.arguments import AppStoreVersionInfo
from codemagic.tools.app_store_connect.arguments import AppStoreVersionLocalizationInfo


@mock.patch("codemagic.tools.AppStoreConnect.api_client")
def test_submit_to_app_store_platform_using_version_info(mock_api_client: mock.MagicMock):
    app_store_connect = AppStoreConnect(
        issuer_id=IssuerId("issuer-id"),
        key_identifier=KeyIdentifier("key-identifier"),
        private_key="private-key",
    )

    build = mock.MagicMock(spec=Build, id=ResourceId("build-id"))
    app = mock.MagicMock(spec=App, id=ResourceId("app-id"))
    pre_release_version = mock.MagicMock(spec=PreReleaseVersion, id=ResourceId("pre-release-version-id"))
    app_store_version = mock.MagicMock(spec=AppStoreVersion, id=ResourceId("app-store-version-id"))
    review_submission = mock.MagicMock(spec=ReviewSubmission, id=ResourceId("review-submission-id"))
    review_submission_item = mock.MagicMock(spec=ReviewSubmissionItem, id=ResourceId("review-submission-item-id"))

    mock_api_client.builds.read_with_include.return_value = (build, app)

    with mock.patch.object(
        app_store_connect,
        "_cancel_previous_submissions",
    ) as mock_cancel_previous_submissions, mock.patch.object(
        app_store_connect,
        "wait_until_build_is_processed",
    ) as mock_wait_until_build_is_processed, mock.patch.object(
        app_store_connect,
        "get_build_pre_release_version",
        return_value=pre_release_version,
    ), mock.patch.object(
        app_store_connect,
        "_ensure_app_store_version",
        return_value=app_store_version,
    ), mock.patch.object(
        app_store_connect,
        "_manage_app_store_version_phased_release",
    ) as mock_manage_app_store_version_phased_release, mock.patch.object(
        app_store_connect,
        "_create_or_update_app_store_version_localizations",
    ), mock.patch.object(
        app_store_connect,
        "_create_review_submission",
        return_value=review_submission,
    ) as mock_create_review_submission, mock.patch.object(
        app_store_connect,
        "create_review_submission_item",
        return_value=review_submission_item,
    ) as mock_create_review_submission_item, mock.patch.object(
        app_store_connect,
        "confirm_review_submission",
    ) as mock_confirm_review_submission:
        created_review_submission, created_review_submission_item = app_store_connect.submit_to_app_store(
            build.id,
            max_build_processing_wait=23,
            cancel_previous_submissions=True,
            app_store_version_info=AppStoreVersionInfo(
                platform=Platform.MAC_OS,
                version_string="1.2.3",
                release_type=ReleaseType.AFTER_APPROVAL,
                earliest_release_date=None,
                copyright=None,
            ),
            app_store_version_localizations=[
                AppStoreVersionLocalizationInfo(
                    locale=Locale.EN_GB,
                    whats_new="Whats new in English",
                ),
            ],
            enable_phased_release=True,
            disable_phased_release=None,
        )

    mock_api_client.builds.read_with_include.assert_called_once_with(build.id, App)
    mock_cancel_previous_submissions.assert_called_once_with(build, Platform.MAC_OS)
    mock_wait_until_build_is_processed.assert_called_once_with(build, 23)
    mock_manage_app_store_version_phased_release.assert_called_once_with(app_store_version, True)
    mock_create_review_submission.assert_called_once_with(app, Platform.MAC_OS)
    mock_create_review_submission_item.assert_called_once_with(
        review_submission_id=review_submission.id,
        app_store_version_id=app_store_version.id,
    )
    mock_confirm_review_submission.assert_called_once_with(review_submission.id)
    assert created_review_submission == review_submission
    assert created_review_submission_item == review_submission_item
