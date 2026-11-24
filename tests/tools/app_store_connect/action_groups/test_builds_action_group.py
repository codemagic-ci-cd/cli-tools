import time
from unittest import mock

from requests import ReadTimeout

from codemagic.apple.resources import BuildProcessingState
from codemagic.tools import AppStoreConnect


def _build(processing_state: BuildProcessingState) -> mock.Mock:
    return mock.Mock(id="build-id", attributes=mock.Mock(processingState=processing_state))


def test_wait_until_build_is_processed_continues_after_timeout(mock_app_store_connect: AppStoreConnect):
    processed_build = _build(BuildProcessingState.VALID)
    api_client = mock.Mock()
    api_client.builds.read.side_effect = (ReadTimeout("Read timed out."), processed_build)

    with mock.patch.object(AppStoreConnect, "api_client", new_callable=mock.PropertyMock, return_value=api_client):
        build = mock_app_store_connect._wait_until_build_is_processed(
            _build(BuildProcessingState.PROCESSING),
            processing_started_at=time.time(),
            max_processing_minutes=1,
            retry_wait_seconds=0,
        )

    assert build is processed_build
    assert api_client.builds.read.call_count == 2


def test_wait_until_build_beta_detail_is_processed_continues_after_timeout(mock_app_store_connect: AppStoreConnect):
    build_beta_detail = mock.Mock()
    api_client = mock.Mock()
    api_client.builds.read_beta_detail.side_effect = (ReadTimeout("Read timed out."), build_beta_detail)

    with mock.patch.object(AppStoreConnect, "api_client", new_callable=mock.PropertyMock, return_value=api_client):
        result = mock_app_store_connect._wait_until_build_beta_detail_is_processed(
            _build(BuildProcessingState.VALID),
            processing_started_at=time.time(),
            max_processing_minutes=1,
            retry_wait_seconds=0,
        )

    assert result is build_beta_detail
    assert api_client.builds.read_beta_detail.call_count == 2
