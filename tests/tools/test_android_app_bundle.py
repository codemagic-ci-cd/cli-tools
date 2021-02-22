from __future__ import annotations

import argparse
import itertools
import pathlib
import re
from unittest import mock

import pytest

from codemagic.tools.android_app_bundle import AndroidAppBundle
from codemagic.tools.android_app_bundle import AndroidAppBundleArgument
from codemagic.tools.android_app_bundle import AndroidAppBundleTypes

SIGNING_INFO_ARGS = (
    (AndroidAppBundleArgument.KEYSTORE_PATH, pathlib.Path('keystore.jks')),
    (AndroidAppBundleArgument.KEYSTORE_PASSWORD, AndroidAppBundleTypes.KeystorePassword('keystore password')),
    (AndroidAppBundleArgument.KEY_ALIAS, AndroidAppBundleTypes.KeyAlias('key alias')),
    (AndroidAppBundleArgument.KEY_PASSWORD, AndroidAppBundleTypes.KeyPassword('key password')),
)


@pytest.fixture(scope='module')
def android_app_bundle():
    return AndroidAppBundle()


def mock_find_paths(_self, *args):
    return [*args]


def mock_build_apk_set_archive(_self, aab_path, *, signing_info=None, mode=None):
    is_signed = 'signed' if signing_info else 'unsigned'
    return pathlib.Path(aab_path.parent, f'{aab_path.stem}-{is_signed}.apks')


@pytest.mark.parametrize('signing_info_args', itertools.chain(
    itertools.combinations(SIGNING_INFO_ARGS, 1),
    itertools.combinations(SIGNING_INFO_ARGS, 2),
    itertools.combinations(SIGNING_INFO_ARGS, 3),
))
@mock.patch.object(AndroidAppBundle, 'find_paths', mock_find_paths)
def test_build_apks_incomplete_signing_info_arg(signing_info_args, android_app_bundle, cli_argument_group):
    signing_info_kwargs = {}
    for signing_info_arg, signing_info_arg_value in signing_info_args:
        signing_info_arg.register(cli_argument_group)
        signing_info_kwargs[signing_info_arg.key] = signing_info_arg_value

    with pytest.raises(argparse.ArgumentError) as exception_info:
        android_app_bundle.build_apks(pathlib.Path('android_app_bundle.aab'), **signing_info_kwargs)

    expected_invalid_flag = AndroidAppBundleArgument.KEYSTORE_PATH.flags[0]
    expected_error_message = 'Either all signing info arguments should be specified, or none of them should'
    assert exception_info.value.argument_name == expected_invalid_flag
    assert exception_info.value.message == expected_error_message


@mock.patch.object(AndroidAppBundle, 'find_paths', mock_find_paths)
def test_build_apks_no_signing_info_args(android_app_bundle):
    with mock.patch.object(AndroidAppBundle, '_build_apk_set_archive', mock_build_apk_set_archive):
        built_apks = android_app_bundle.build_apks(pathlib.Path('android_app_bundle.aab'))
    assert built_apks == [pathlib.Path('android_app_bundle-unsigned.apks')]


@mock.patch.object(AndroidAppBundle, 'find_paths', mock_find_paths)
def test_build_apks_signing_info_args(android_app_bundle, cli_argument_group):
    signing_info_kwargs = {}
    for signing_info_arg, signing_info_arg_value in SIGNING_INFO_ARGS:
        signing_info_arg.register(cli_argument_group)
        signing_info_kwargs[signing_info_arg.key] = signing_info_arg_value

    with mock.patch.object(AndroidAppBundle, '_build_apk_set_archive', mock_build_apk_set_archive):
        built_apks = android_app_bundle.build_apks(
            pathlib.Path('android_app_bundle.aab'),
            **signing_info_kwargs,
        )
    assert built_apks == [pathlib.Path('android_app_bundle-signed.apks')]


def test_bundletool_jar_executable(android_app_bundle):
    bundletool_version = android_app_bundle.bundletool_version()
    assert re.match(r'^(\d+\.?)+$', bundletool_version) is not None
