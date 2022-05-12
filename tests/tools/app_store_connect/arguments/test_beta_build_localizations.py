import json
import os
import tempfile
from argparse import ArgumentTypeError

import pytest

from codemagic.apple.resources import Locale
from codemagic.models.enums import ResourceEnumMeta
from codemagic.tools.app_store_connect import BetaBuildInfo
from codemagic.tools.app_store_connect import Types


@pytest.fixture()
def valid_input() -> str:
    return json.dumps([
        {
            'locale': 'en-GB',
            'whats_new': 'en-GB notes',
        },
        {
            'locale': 'en-US',
            'whats_new': 'en-US notes',
        },
        {
            'locale': 'fi',
            'whats_new': 'fi notes',
        },
    ])


@pytest.fixture()
def expected_valid_result():
    return [
        BetaBuildInfo(whats_new='en-GB notes', locale=Locale.EN_GB),
        BetaBuildInfo(whats_new='en-US notes', locale=Locale.EN_US),
        BetaBuildInfo(whats_new='fi notes', locale=Locale.FI),
    ]


def test_empty_input():
    beta_build_localizations = Types.BetaBuildLocalizations('[]')
    assert beta_build_localizations.value == []


def test_from_str(valid_input, expected_valid_result):
    beta_build_localizations = Types.BetaBuildLocalizations(valid_input)
    assert beta_build_localizations.value == expected_valid_result


def test_env_default(valid_input, expected_valid_result):
    os.environ[Types.BetaBuildLocalizations.environment_variable_key] = valid_input
    beta_build_localizations = Types.BetaBuildLocalizations.from_environment_variable_default()
    assert beta_build_localizations.value == expected_valid_result


def test_from_env(valid_input, expected_valid_result):
    env_var = 'WHATS_NEW'
    os.environ[env_var] = valid_input
    beta_build_localizations = Types.BetaBuildLocalizations(f'@env:{env_var}')
    assert beta_build_localizations.value == expected_valid_result


def test_from_file(valid_input, expected_valid_result):
    with tempfile.NamedTemporaryFile() as tf:
        tf.write(valid_input.encode())
        tf.flush()
        beta_build_localizations = Types.BetaBuildLocalizations(f'@file:{tf.name}')
    assert beta_build_localizations.value == expected_valid_result


@pytest.mark.parametrize('given_input, expected_error', [
    ('{P}', "Provided value '{P}' is not a valid JSON encoded list"),
    ('1', "Provided value '1' is not a valid JSON encoded list"),
    ('{}', "Provided value '{}' is not a valid JSON encoded list"),
    ('Some string', "Provided value 'Some string' is not a valid JSON encoded list"),
    ('', "Provided value '' is not a valid JSON encoded list"),
    ('[{"whats_new": "..."}]', "Invalid beta build localization on index 0, missing locale in {'whats_new': '...'}"),
    ('[{"locale": "en-US"}]', "Invalid beta build localization on index 0, missing whats_new in {'locale': 'en-US'}"),
    (
        '[{"locale": "il", "whats_new": "?"}]',
        "Invalid beta build localization on index 0, 'il' is not a valid Locale in {'locale': 'il', 'whats_new': '?'}",
    ),
    (
        '[{"locale": "en-US", "whats_new": "..."}, {}]',
        'Invalid beta build localization on index 1, missing whats_new in {}',
    ),
    (
        '[{"locale": "fi", "whats_new": "..."}, {"locale": "fi", "whats_new": "..."}]',
        'Ambiguous definitions for locale(s) fi. Please define beta build localization for each locale exactly once.',
    ),
    ('[{"locale": "en-US", "whats_new": "..."}, 1]', 'Invalid beta build localization value 1 on index 1'),
    ('[{"locale": "en-US", "whats_new": "..."}, []]', 'Invalid beta build localization value [] on index 1'),
    (
        '[{"locale": "en-US", "whats_new": "..."}, "lorem ipsum"]',
        "Invalid beta build localization value 'lorem ipsum' on index 1",
    ),
])
def test_invalid_input(given_input, expected_error):
    with ResourceEnumMeta.without_graceful_fallback():
        with pytest.raises(ArgumentTypeError) as exc_info:
            Types.BetaBuildLocalizations(given_input)
    assert str(exc_info.value) == expected_error
