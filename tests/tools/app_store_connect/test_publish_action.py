from __future__ import annotations

import argparse
import os
import pathlib
from unittest import mock

import pytest

from codemagic.apple.resources import Locale
from codemagic.apple.resources import Platform
from codemagic.apple.resources import ReleaseType
from codemagic.models.application_package import Ipa
from codemagic.tools.app_store_connect import AppStoreConnect
from codemagic.tools.app_store_connect import AppStoreConnectArgument
from codemagic.tools.app_store_connect import PublishArgument
from codemagic.tools.app_store_connect import Types


@pytest.fixture()
def publishing_namespace_kwargs(namespace_kwargs):
    namespace_kwargs.update({
        'action': 'publish',
    })
    return namespace_kwargs


def test_publish_action_without_app_store_connect_key(publishing_namespace_kwargs):
    publishing_namespace_kwargs.update({
        AppStoreConnectArgument.ISSUER_ID.key: None,
        AppStoreConnectArgument.KEY_IDENTIFIER.key: None,
        AppStoreConnectArgument.PRIVATE_KEY.key: None,
    })
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    _ = AppStoreConnect.from_cli_args(cli_args)


@pytest.mark.parametrize('missing_argument', [
    AppStoreConnectArgument.ISSUER_ID,
    AppStoreConnectArgument.KEY_IDENTIFIER,
    AppStoreConnectArgument.PRIVATE_KEY,
])
def test_publish_action_without_app_store_connect_key_testflight_submit(missing_argument, publishing_namespace_kwargs):
    publishing_namespace_kwargs.update({missing_argument.key: None})
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    app_store_connect = AppStoreConnect.from_cli_args(cli_args)
    with pytest.raises(argparse.ArgumentError) as error_info:
        app_store_connect.publish(
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            application_package_path_patterns=[pathlib.Path('path.pattern')],
            submit_to_testflight=True,
        )
    assert missing_argument.flag in error_info.value.argument_name


@pytest.mark.parametrize('missing_argument', [
    AppStoreConnectArgument.ISSUER_ID,
    AppStoreConnectArgument.KEY_IDENTIFIER,
    AppStoreConnectArgument.PRIVATE_KEY,
])
def test_publish_action_without_app_store_connect_key_and_beta_locales(missing_argument, publishing_namespace_kwargs):
    publishing_namespace_kwargs.update({missing_argument.key: None})
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    app_store_connect = AppStoreConnect.from_cli_args(cli_args)
    with pytest.raises(argparse.ArgumentError) as error_info:
        app_store_connect.publish(
            application_package_path_patterns=[pathlib.Path('path.pattern')],
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            beta_build_localizations=Types.BetaBuildLocalizations('[]'),
        )
    assert missing_argument.flag in error_info.value.argument_name


@mock.patch('codemagic.tools._app_store_connect.actions.publish_action.Altool')
def test_publish_action_with_username_and_password(_mock_altool, publishing_namespace_kwargs):
    publishing_namespace_kwargs.update({
        AppStoreConnectArgument.ISSUER_ID.key: None,
        AppStoreConnectArgument.KEY_IDENTIFIER.key: None,
        AppStoreConnectArgument.PRIVATE_KEY.key: None,
    })

    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
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


def test_publish_action_testflight_with_localization(publishing_namespace_kwargs):
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_assert_app_has_testflight_information'), \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build_application') as mock_get_app, \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build') as mock_get_build, \
            mock.patch.object(AppStoreConnect, 'wait_until_build_is_processed') as mock_wait_until_build_is_processed, \
            mock.patch.object(AppStoreConnect, 'submit_to_testflight') as mock_submit_to_testflight, \
            mock.patch.object(AppStoreConnect, 'submit_to_app_store') as mock_submit_to_app_store, \
            mock.patch.object(AppStoreConnect, 'add_beta_test_info') as mock_add_beta_test_info:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_get_packages.return_value = [mock.create_autospec(Ipa, instance=True, path=ipa_path)]
        build = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_app.return_value = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_build.return_value = build
        locale = Locale('en-GB')

        whats_new = Types.WhatsNewArgument("What's new")
        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            submit_to_testflight=True,
            locale=locale,
            whats_new=whats_new,
        )

        mock_get_packages.assert_called_with(patterns)
        mock_validate.assert_not_called()
        mock_upload.assert_called()
        mock_wait_until_build_is_processed.assert_called_with(build, Types.MaxBuildProcessingWait.default_value)
        mock_submit_to_testflight.assert_called_with(build.id, max_build_processing_wait=0)
        mock_submit_to_app_store.assert_not_called()
        mock_add_beta_test_info.assert_called_with(
            build.id,
            beta_build_localizations=None,
            locale=locale,
            whats_new=whats_new,
        )


def test_publish_action_app_store_submit(publishing_namespace_kwargs):
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_assert_app_has_testflight_information'), \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build_application') as mock_get_app, \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build') as mock_get_build, \
            mock.patch.object(AppStoreConnect, 'wait_until_build_is_processed') as mock_wait_until_build_is_processed, \
            mock.patch.object(AppStoreConnect, 'submit_to_testflight') as mock_submit_to_testflight, \
            mock.patch.object(AppStoreConnect, 'submit_to_app_store') as mock_submit_to_app_store, \
            mock.patch.object(AppStoreConnect, 'add_beta_test_info') as mock_add_beta_test_info:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_ipa = mock.create_autospec(Ipa, instance=True, path=ipa_path, version='1.2.3')
        mock_ipa.is_for_tvos = lambda: False
        mock_get_packages.return_value = [mock_ipa]
        build = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_app.return_value = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_build.return_value = build

        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            submit_to_app_store=True,
            max_build_processing_wait=Types.MaxBuildProcessingWait('5'),
            release_type=ReleaseType.AFTER_APPROVAL,
        )

        mock_get_packages.assert_called_with(patterns)
        mock_validate.assert_not_called()
        mock_upload.assert_called()
        mock_wait_until_build_is_processed.assert_called_with(build, 5)
        mock_submit_to_testflight.assert_not_called()
        mock_submit_to_app_store.assert_called_with(
            build.id,
            max_build_processing_wait=0,
            # General App Store version info
            copyright=None,
            earliest_release_date=None,
            platform=Platform.IOS,
            release_type=ReleaseType.AFTER_APPROVAL,
            version_string='1.2.3',
            # Localized App Store version information
            app_store_version_info=None,
            app_store_version_localizations=None,
            description=None,
            keywords=None,
            locale=None,
            marketing_url=None,
            promotional_text=None,
            support_url=None,
            whats_new=None,
        )
        mock_add_beta_test_info.assert_not_called()


@mock.patch('codemagic.tools._app_store_connect.actions.publish_action.Altool')
@pytest.mark.parametrize('enable_package_validation, should_validate', [
    (True, True),
    (False, False),
    (None, False),
])
def test_publish_action_enable_validation(_mock_altool, namespace_kwargs, enable_package_validation, should_validate):
    asc = AppStoreConnect.from_cli_args(argparse.Namespace(**namespace_kwargs))
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_get_packages.return_value = [mock.create_autospec(Ipa, instance=True, path=ipa_path)]

        asc.publish(
            application_package_path_patterns=[ipa_path],
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            enable_package_validation=enable_package_validation,
        )

        mock_upload.assert_called()
        if should_validate:
            mock_validate.assert_called()
        else:
            mock_validate.assert_not_called()


@pytest.mark.parametrize('argument', (PublishArgument.SKIP_PACKAGE_VALIDATION, PublishArgument.SKIP_PACKAGE_UPLOAD))
@pytest.mark.parametrize('environment_value', ['1', 'true', 'True', 'false', 'asdf', '   ', 'null', 'None'])
def test_skip_package_upload_or_validation_argument_from_env(argument, environment_value):
    """
    Since this is a boolean switch any "truthy" string will resolve so that the switch will be turned on.
    """
    args = argparse.Namespace(**{argument.key: None})
    os.environ[argument.type.environment_variable_key] = environment_value
    parsed_value = argument.from_args(args)
    assert parsed_value.value is True


@pytest.mark.parametrize(
    'argument',
    (
        PublishArgument.SKIP_PACKAGE_VALIDATION,
        PublishArgument.SKIP_PACKAGE_UPLOAD,
    ),
)
def test_no_skip_package_upload_or_validation_argument_from_env(cli_argument_group, argument):
    """
    Non "truthy" value is not valid as this action just turns the switch on.
    """
    argument.register(cli_argument_group)
    args = argparse.Namespace(**{argument.key: None})
    os.environ[argument.type.environment_variable_key] = ''
    with pytest.raises(argparse.ArgumentError) as error_info:
        argument.from_args(args)
    assert str(error_info.value) == f'argument {"/".join(argument.flags)}: Provided value "" is not valid'


def test_add_build_to_beta_groups(publishing_namespace_kwargs):
    cli_args = argparse.Namespace(**publishing_namespace_kwargs)
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build_application') as mock_get_app, \
            mock.patch.object(AppStoreConnect, '_get_uploaded_build') as mock_get_build, \
            mock.patch.object(AppStoreConnect, 'submit_to_testflight') as mock_submit_to_testflight, \
            mock.patch.object(AppStoreConnect, 'submit_to_app_store') as mock_submit_to_app_store, \
            mock.patch.object(AppStoreConnect, 'wait_until_build_is_processed') as mock_wait_until_build_is_processed, \
            mock.patch.object(AppStoreConnect, 'add_build_to_beta_groups') as mock_add_build_to_beta_groups:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_get_packages.return_value = [mock.create_autospec(Ipa, instance=True, path=ipa_path)]
        build = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_app.return_value = mock.Mock(id='1525e3c9-3015-407a-9ba5-9addd2558224')
        mock_get_build.return_value = build

        beta_group_names = ['Test group 1', 'Test group 2']
        patterns = [pathlib.Path('path.pattern')]
        AppStoreConnect.from_cli_args(cli_args).publish(
            application_package_path_patterns=patterns,
            submit_to_testflight=True,
            beta_group_names=beta_group_names,
        )

        mock_get_packages.assert_called_with(patterns)
        mock_validate.assert_not_called()
        mock_upload.assert_called()
        mock_wait_until_build_is_processed.assert_called_with(build, Types.MaxBuildProcessingWait.default_value)
        mock_submit_to_testflight.assert_called_with(build.id, max_build_processing_wait=0)
        mock_submit_to_app_store.assert_not_called()
        mock_add_build_to_beta_groups.assert_called_with(build.id, beta_group_names=beta_group_names)
