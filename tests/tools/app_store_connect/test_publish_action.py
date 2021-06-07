from __future__ import annotations

import argparse
import os
import pathlib
from unittest import mock

import pytest

from codemagic.tools._app_store_connect.arguments import PublishArgument
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


@mock.patch('codemagic.tools._app_store_connect.actions.publish_action.Altool')
@pytest.mark.parametrize('skip_package_validation, should_validate', [
    (True, False),
    (False, True),
    (None, True),
])
def test_publish_action_skip_validation(_mock_altool, namespace_kwargs, skip_package_validation, should_validate):
    class MockIpa:
        def __init__(self, path: pathlib.Path):
            self.path = path

        @classmethod
        def get_text_summary(cls):
            return ''

    asc = AppStoreConnect.from_cli_args(argparse.Namespace(**namespace_kwargs))
    with mock.patch.object(AppStoreConnect, 'find_paths') as mock_find_paths, \
            mock.patch.object(AppStoreConnect, '_get_publishing_application_packages') as mock_get_packages, \
            mock.patch.object(AppStoreConnect, '_validate_artifact_with_altool') as mock_validate, \
            mock.patch.object(AppStoreConnect, '_upload_artifact_with_altool') as mock_upload:
        ipa_path = pathlib.Path('app.ipa')
        mock_find_paths.return_value = [ipa_path]
        mock_get_packages.return_value = [MockIpa(ipa_path)]

        asc.publish(
            application_package_path_patterns=[ipa_path],
            apple_id='name@example.com',
            app_specific_password=Types.AppSpecificPassword('xxxx-yyyy-zzzz-wwww'),
            skip_package_validation=skip_package_validation,
        )

        mock_upload.assert_called()
        if should_validate:
            mock_validate.assert_called()
        else:
            mock_validate.assert_not_called()


@pytest.mark.parametrize('environment_value', ['1', 'true', 'True', 'false', 'asdf', '   ', 'null', 'None'])
def test_skip_package_validation_argument_from_env(environment_value):
    """
    Since this is a boolean switch any "truthy" string will resolve so that the switch will be turned on.
    """
    args = argparse.Namespace(skip_package_validation=None)
    os.environ[Types.AppStoreConnectSkipPackageValidation.environment_variable_key] = environment_value
    parsed_value = PublishArgument.SKIP_PACKAGE_VALIDATION.from_args(args)
    assert parsed_value.value is True


def test_no_skip_package_validation_argument_from_env(cli_argument_group):
    """
    Non "truthy" value is not valid as this action just turns the switch on.
    """
    PublishArgument.SKIP_PACKAGE_VALIDATION.register(cli_argument_group)
    args = argparse.Namespace(skip_package_validation=None)
    os.environ[Types.AppStoreConnectSkipPackageValidation.environment_variable_key] = ''
    with pytest.raises(argparse.ArgumentError) as error_info:
        PublishArgument.SKIP_PACKAGE_VALIDATION.from_args(args)
    assert str(error_info.value) == 'argument --skip-package-validation: Provided value "False" is not valid'
