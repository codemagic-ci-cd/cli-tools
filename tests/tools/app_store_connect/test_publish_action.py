from __future__ import annotations

import argparse
import pathlib
from unittest import mock

import pytest

from codemagic.tools.app_store_connect import AppStoreConnect
from codemagic.tools.app_store_connect import AppStoreConnectArgument
from codemagic.tools.app_store_connect import Types


def test_publish_action_without_app_store_connect_key(namespace_kwargs):
    namespace_kwargs.update({
        AppStoreConnectArgument.ISSUER_ID.key: None,
        AppStoreConnectArgument.KEY_IDENTIFIER.key: None,
        AppStoreConnectArgument.PRIVATE_KEY.key: None,
        'action': 'publish',
    })
    cli_args = argparse.Namespace(**namespace_kwargs)
    _ = AppStoreConnect.from_cli_args(cli_args)


@pytest.mark.parametrize('missing_argument', [
    AppStoreConnectArgument.ISSUER_ID,
    AppStoreConnectArgument.KEY_IDENTIFIER,
    AppStoreConnectArgument.PRIVATE_KEY,
])
def test_publish_action_without_app_store_connect_key_testflight_submit(missing_argument, namespace_kwargs):
    namespace_kwargs.update({missing_argument.key: None, 'action': 'publish'})
    cli_args = argparse.Namespace(**namespace_kwargs)
    app_store_connect = AppStoreConnect.from_cli_args(cli_args)
    with pytest.raises(argparse.ArgumentError) as error_info:
        app_store_connect.publish(
            application_package_path_patterns=[pathlib.Path('path.pattern')],
            submit_to_testflight=True,
        )
    assert missing_argument.flag in error_info.value.argument_name


@mock.patch('codemagic.tools._app_store_connect.actions.publish_action.Altool')
def test_publish_action_with_username_and_password(_mock_altool, namespace_kwargs):
    namespace_kwargs.update({
        AppStoreConnectArgument.ISSUER_ID.key: None,
        AppStoreConnectArgument.KEY_IDENTIFIER.key: None,
        AppStoreConnectArgument.PRIVATE_KEY.key: None,
        'action': 'publish',
    })

    cli_args = argparse.Namespace(**namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages:
        mock_get_packages.return_value = []
        mock_find_paths.return_value = []

        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
        )
        mock_get_packages.assert_called_with(patterns)


def test_publish_action_testflight(namespace_kwargs):
    namespace_kwargs.update({'action': 'publish'})

    cli_args = argparse.Namespace(**namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages:
        mock_get_packages.return_value = []
        mock_find_paths.return_value = []

        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            submit_to_testflight=True,
        )
        mock_get_packages.assert_called_with(patterns)


@pytest.mark.parametrize('localization_arguments', [{'whats_new': "What's new"}, {'locale': 'en-GB'}])
def test_publish_action_testflight_with_localization_with_missing_key(localization_arguments, namespace_kwargs):
    namespace_kwargs.update({'action': 'publish'})
    cli_args = argparse.Namespace(**namespace_kwargs)
    patterns = [pathlib.Path('path.pattern')]

    with pytest.raises(IOError) as error_info:
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            submit_to_testflight=True,
            **localization_arguments,
        )

    assert str(error_info.value) \
        == 'Both --locale and --whats-new need to be defined for providing beta build localization'


def test_publish_action_with_localization_and_no_testflight_submission(namespace_kwargs):
    namespace_kwargs.update({'action': 'publish'})
    cli_args = argparse.Namespace(**namespace_kwargs)
    patterns = [pathlib.Path('path.pattern')]

    with pytest.raises(IOError) as error_info:
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            locale='en-GB',
            whats_new="What's new",
        )

    assert str(error_info.value) \
        == '--testflight flag is required for providing beta build localization'


def test_publish_action_testflight_with_localization(namespace_kwargs):
    class MockBuild:
        def __init__(self, build_id):
            self.id = build_id

    class MockIpa:
        def __init__(self, path: pathlib.Path):
            self.path = path

        @staticmethod
        def get_text_summary():
            return ''

    namespace_kwargs.update({'action': 'publish'})

    cli_args = argparse.Namespace(**namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build') as mock_get_build, \
            mock.patch.object(AppStoreConnect, 'create_beta_app_review_submission') as mock_create_review, \
            mock.patch.object(AppStoreConnect, 'create_beta_build_localization') as mock_create_localization:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_get_packages.return_value = [MockIpa(ipa_path)]
        build = MockBuild('1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_build.return_value = [build, '1.0.0']

        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            submit_to_testflight=True,
            locale='en-GB',
            whats_new="What's new",
        )
        mock_validate.assert_called()
        mock_upload.assert_called()
        mock_create_review.assert_called_with(build.id)
        mock_get_packages.assert_called_with(patterns)
        mock_create_localization.assert_called_with(build.id, 'en-GB', "What's new")
