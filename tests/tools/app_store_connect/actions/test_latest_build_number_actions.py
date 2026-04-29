from unittest import mock

from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import ResourceId
from codemagic.tools import AppStoreConnect
from codemagic.tools.app_store_connect.actions.latest_build_number_actions import _LatestBuildInfo


def _make_app_store_connect() -> AppStoreConnect:
    return AppStoreConnect(
        issuer_id=IssuerId("issuer-id"),
        key_identifier=KeyIdentifier("key-identifier"),
        private_key="private-key",
    )


@mock.patch("codemagic.tools.AppStoreConnect.api_client")
def test_get_latest_build_number_forwards_version_to_both_sides(_mock_api_client: mock.MagicMock):
    app_store_connect = _make_app_store_connect()
    application_id = ResourceId("application-id")

    asc_info = _LatestBuildInfo(
        build_id="asc-build-id",
        build_number="42",
        app_store_version="1.0.0",
    )
    tf_info = _LatestBuildInfo(
        build_id="tf-build-id",
        build_number="43",
        pre_release_version="1.0.0",
    )

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
        return_value=asc_info,
    ) as mock_app_store, mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
        return_value=tf_info,
    ) as mock_testflight, mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_build_number(application_id, version="1.0.0")

    mock_app_store.assert_called_once_with(
        application_id,
        version_string="1.0.0",
        platform=None,
    )
    mock_testflight.assert_called_once_with(
        application_id,
        pre_release_version="1.0.0",
        platform=None,
    )
    assert result == "43"


@mock.patch("codemagic.tools.AppStoreConnect.api_client")
def test_get_latest_build_number_without_version_passes_none(_mock_api_client: mock.MagicMock):
    app_store_connect = _make_app_store_connect()
    application_id = ResourceId("application-id")

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
        return_value=None,
    ) as mock_app_store, mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
        return_value=None,
    ) as mock_testflight:
        result = app_store_connect.get_latest_build_number(application_id)

    mock_app_store.assert_called_once_with(
        application_id,
        version_string=None,
        platform=None,
    )
    mock_testflight.assert_called_once_with(
        application_id,
        pre_release_version=None,
        platform=None,
    )
    assert result is None


@mock.patch("codemagic.tools.AppStoreConnect.api_client")
def test_get_latest_build_number_returns_match_when_only_one_side_has_build(
    _mock_api_client: mock.MagicMock,
):
    app_store_connect = _make_app_store_connect()
    application_id = ResourceId("application-id")

    tf_info = _LatestBuildInfo(
        build_id="tf-build-id",
        build_number="7",
        pre_release_version="2.0.0",
    )

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
        return_value=None,
    ), mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
        return_value=tf_info,
    ), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_build_number(application_id, version="2.0.0")

    assert result == "7"
