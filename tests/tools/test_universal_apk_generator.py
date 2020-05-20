from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pytest

from codemagic.tools.universal_apk_generator import UniversalApkGenerator
from codemagic.tools.universal_apk_generator import UniversalApkGeneratorArgument

SIGNING_INFO_ARGS = (
    UniversalApkGeneratorArgument.KEYSTORE_PATH,
    UniversalApkGeneratorArgument.KEYSTORE_PASSWORD,
    UniversalApkGeneratorArgument.KEY_ALIAS,
    UniversalApkGeneratorArgument.KEY_PASSWORD,
)


@pytest.fixture
def namespace_kwargs():
    return {
        UniversalApkGeneratorArgument.PATTERN.key: Path('**/*.aab'),
    }


@pytest.mark.parametrize('cli_args', itertools.chain(
    itertools.combinations(SIGNING_INFO_ARGS, 1),
    itertools.combinations(SIGNING_INFO_ARGS, 2),
    itertools.combinations(SIGNING_INFO_ARGS, 3),
))
def test_incomplete_signing_info_args(cli_args, cli_argument_group, namespace_kwargs):
    for arg in SIGNING_INFO_ARGS:
        namespace_kwargs[arg.key] = arg.key if arg in cli_args else None
        arg.register(cli_argument_group)

    cli_namespace = argparse.Namespace(**namespace_kwargs)
    with pytest.raises(argparse.ArgumentError) as exception_info:
        UniversalApkGenerator.from_cli_args(cli_namespace)
    assert exception_info.value.argument_name in UniversalApkGeneratorArgument.KEYSTORE_PATH.flags
    assert 'all signing info arguments should be specified' in exception_info.value.message


def test_no_signing_info_args(cli_argument_group, namespace_kwargs):
    for arg in SIGNING_INFO_ARGS:
        namespace_kwargs[arg.key] = None

    cli_namespace = argparse.Namespace(**namespace_kwargs)
    uag = UniversalApkGenerator.from_cli_args(cli_namespace)
    assert uag.android_signing_info is None


def test_signing_info_args(cli_argument_group, namespace_kwargs):
    for arg in SIGNING_INFO_ARGS:
        namespace_kwargs[arg.key] = arg.key

    cli_namespace = argparse.Namespace(**namespace_kwargs)
    uag = UniversalApkGenerator.from_cli_args(cli_namespace)
    assert uag.android_signing_info is not None
    assert uag.android_signing_info.store_path == UniversalApkGeneratorArgument.KEYSTORE_PATH.key
    assert uag.android_signing_info.store_pass == UniversalApkGeneratorArgument.KEYSTORE_PASSWORD.key
    assert uag.android_signing_info.key_alias == UniversalApkGeneratorArgument.KEY_ALIAS.key
    assert uag.android_signing_info.key_pass == UniversalApkGeneratorArgument.KEY_PASSWORD.key
