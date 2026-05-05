import argparse
from unittest import mock

import pytest

from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import ResourceId
from codemagic.tools import AppStoreConnect
from codemagic.tools.app_store_connect.actions.latest_build_number_actions import _LatestBuildInfo


@pytest.fixture
def app_store_connect() -> AppStoreConnect:
    return AppStoreConnect(
        issuer_id=IssuerId("issuer-id"),
        key_identifier=KeyIdentifier("key-identifier"),
        private_key="private-key",
    )


def test_get_latest_build_number_forwards_version_to_both_sides(app_store_connect: AppStoreConnect):
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
        all_versions=False,
    )
    mock_testflight.assert_called_once_with(
        application_id,
        pre_release_version="1.0.0",
        platform=None,
        all_versions=False,
    )
    assert result == "43"


def test_get_latest_build_number_without_version_passes_none(app_store_connect: AppStoreConnect):
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
        all_versions=False,
    )
    mock_testflight.assert_called_once_with(
        application_id,
        pre_release_version=None,
        platform=None,
        all_versions=False,
    )
    assert result is None


def test_get_latest_build_number_returns_match_when_only_one_side_has_build(
    app_store_connect: AppStoreConnect,
):
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


def test_get_latest_build_number_picks_higher_build_when_versions_equal(
    app_store_connect: AppStoreConnect,
):
    application_id = ResourceId("application-id")

    asc_info = _LatestBuildInfo(
        build_id="asc-build-id",
        build_number="120",
        app_store_version="3.2.46",
    )
    tf_info = _LatestBuildInfo(
        build_id="tf-build-id",
        build_number="90",
        pre_release_version="3.2.46",
    )

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
        return_value=asc_info,
    ), mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
        return_value=tf_info,
    ), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_build_number(application_id, version="3.2.46")

    assert result == "120"


def test_get_latest_build_number_all_versions_tiebreak_uses_build_number(app_store_connect: AppStoreConnect):
    application_id = ResourceId("application-id")

    asc_info = _LatestBuildInfo(
        build_id="asc-build-id",
        build_number="12",
        app_store_version="1.9.0",
    )
    tf_info = _LatestBuildInfo(
        build_id="tf-build-id",
        build_number="5",
        pre_release_version="2.0.0",
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
        result = app_store_connect.get_latest_build_number(application_id, all_versions=True)

    mock_app_store.assert_called_once_with(
        application_id,
        version_string=None,
        platform=None,
        all_versions=True,
    )
    mock_testflight.assert_called_once_with(
        application_id,
        pre_release_version=None,
        platform=None,
        all_versions=True,
    )
    assert result == "12"


def test_get_latest_app_store_build_number_all_versions_picks_global_max(app_store_connect: AppStoreConnect):
    application_id = ResourceId("application-id")

    mock_api = mock.MagicMock()
    mock_api.apps.list_app_store_versions_data.return_value = [
        {"id": "asv1", "attributes": {"versionString": "2.0.0"}},
        {"id": "asv2", "attributes": {"versionString": "1.9.0"}},
    ]
    mock_api.app_store_versions.read_build_data.side_effect = [
        {"id": "build-2.0.0", "attributes": {"version": "5"}},
        {"id": "build-1.9.0", "attributes": {"version": "12"}},
    ]

    with mock.patch.object(app_store_connect, "_get_api_client", return_value=mock_api), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_app_store_build_number(application_id, all_versions=True)

    assert result == "12"
    assert mock_api.app_store_versions.read_build_data.call_count == 2


def test_get_latest_app_store_build_number_without_all_versions_stops_at_first_version(
    app_store_connect: AppStoreConnect,
):
    application_id = ResourceId("application-id")

    mock_api = mock.MagicMock()
    mock_api.apps.list_app_store_versions_data.return_value = [
        {"id": "asv1", "attributes": {"versionString": "2.0.0"}},
        {"id": "asv2", "attributes": {"versionString": "1.9.0"}},
    ]
    mock_api.app_store_versions.read_build_data.side_effect = [
        {"id": "build-2.0.0", "attributes": {"version": "5"}},
        {"id": "build-1.9.0", "attributes": {"version": "12"}},
    ]

    with mock.patch.object(app_store_connect, "_get_api_client", return_value=mock_api), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_app_store_build_number(application_id)

    assert result == "5"
    assert mock_api.app_store_versions.read_build_data.call_count == 1


def test_get_latest_testflight_build_number_all_versions_picks_global_max(app_store_connect: AppStoreConnect):
    application_id = ResourceId("application-id")

    mock_api = mock.MagicMock()
    mock_api.pre_release_versions.list_data.return_value = [
        {"id": "prv1", "attributes": {"version": "2.0.0"}},
        {"id": "prv2", "attributes": {"version": "1.9.0"}},
    ]
    mock_api.pre_release_versions.list_builds_data.side_effect = [
        [{"id": "b1", "attributes": {"version": "5"}}],
        [{"id": "b2", "attributes": {"version": "12"}}],
    ]

    with mock.patch.object(app_store_connect, "_get_api_client", return_value=mock_api), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_testflight_build_number(application_id, all_versions=True)

    assert result == "12"
    assert mock_api.pre_release_versions.list_builds_data.call_count == 2


def test_get_latest_testflight_build_number_without_all_versions_stops_at_first_version(
    app_store_connect: AppStoreConnect,
):
    application_id = ResourceId("application-id")

    mock_api = mock.MagicMock()
    mock_api.pre_release_versions.list_data.return_value = [
        {"id": "prv1", "attributes": {"version": "2.0.0"}},
        {"id": "prv2", "attributes": {"version": "1.9.0"}},
    ]
    mock_api.pre_release_versions.list_builds_data.side_effect = [
        [{"id": "b1", "attributes": {"version": "5"}}],
        [{"id": "b2", "attributes": {"version": "12"}}],
    ]

    with mock.patch.object(app_store_connect, "_get_api_client", return_value=mock_api), mock.patch.object(
        app_store_connect,
        "_log_latest_build_info",
    ):
        result = app_store_connect.get_latest_testflight_build_number(application_id)

    assert result == "5"
    assert mock_api.pre_release_versions.list_builds_data.call_count == 1


def test_get_latest_build_number_with_all_versions_and_version_raises(app_store_connect: AppStoreConnect):
    application_id = ResourceId("application-id")

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
    ) as mock_app_store, mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
    ) as mock_testflight, pytest.raises((argparse.ArgumentError, AttributeError)):
        app_store_connect.get_latest_build_number(application_id, version="1.0.0", all_versions=True)

    mock_app_store.assert_not_called()
    mock_testflight.assert_not_called()


def test_get_latest_app_store_build_number_with_all_versions_and_version_string_raises(
    app_store_connect: AppStoreConnect,
):
    application_id = ResourceId("application-id")

    with mock.patch.object(
        app_store_connect,
        "_get_app_store_latest_build_info",
    ) as mock_app_store, pytest.raises((argparse.ArgumentError, AttributeError)):
        app_store_connect.get_latest_app_store_build_number(
            application_id,
            version_string="1.0.0",
            all_versions=True,
        )

    mock_app_store.assert_not_called()


def test_get_latest_testflight_build_number_with_all_versions_and_pre_release_version_raises(
    app_store_connect: AppStoreConnect,
):
    application_id = ResourceId("application-id")

    with mock.patch.object(
        app_store_connect,
        "_get_testflight_latest_build_info",
    ) as mock_testflight, pytest.raises((argparse.ArgumentError, AttributeError)):
        app_store_connect.get_latest_testflight_build_number(
            application_id,
            pre_release_version="1.0.0",
            all_versions=True,
        )

    mock_testflight.assert_not_called()
