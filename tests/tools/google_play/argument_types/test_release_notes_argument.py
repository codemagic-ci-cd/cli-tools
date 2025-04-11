import argparse
import json

import pytest

from codemagic.google.resources.google_play import Language
from codemagic.google.resources.google_play import LocalizedText
from codemagic.tools.google_play.argument_types import ReleaseNotesArgument


def test_valid_release_notes():
    argument_value = json.dumps(
        [
            {"language": "en-US", "text": "US notes"},
            {"language": "et", "text": "ET notes"},
            {"language": "fi-FI", "text": "FI notes"},
        ],
    )
    release_notes_argument = ReleaseNotesArgument(argument_value)
    assert release_notes_argument.value == [
        LocalizedText(language=Language.ENGLISH_UNITED_STATES, text="US notes"),
        LocalizedText(language=Language.ESTONIAN, text="ET notes"),
        LocalizedText(language=Language.FINNISH, text="FI notes"),
    ]


def test_empty_release_notes():
    release_notes_argument = ReleaseNotesArgument("[]")
    assert release_notes_argument.value == []


@pytest.mark.parametrize(
    ("invalid_argument_value", "expected_error"),
    (
        ('[{"language": "en-US"}]', "Invalid release note on index 0, missing text in {'language': 'en-US'}"),
        ('[{"text": "notes"}]', "Invalid release note on index 0, missing language in {'text': 'notes'}"),
        ("asdf", "Provided value 'asdf' is not a valid JSON encoded list"),
        ("1", "Provided value '1' is not a valid JSON encoded list"),
        (v := '{"langauge": "et", "text": "n"}', f"Provided value '{v}' is not a valid JSON encoded list"),
        ('[{"language": "et", "text": "n"}, 1]', "Invalid release note value 1 on index 1"),
    ),
)
def test_invalid_release_notes(invalid_argument_value, expected_error):
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        ReleaseNotesArgument(invalid_argument_value)
    assert str(exc_info.value) == expected_error


def test_empty_text_release_notes():
    argument_value = json.dumps(
        [
            {"language": "en-US", "text": "US notes"},
            {"language": "et", "text": ""},
            {"language": "fi-FI", "text": "FI notes"},
        ],
    )
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        ReleaseNotesArgument(argument_value)

    assert str(exc_info.value) == "Invalid release note on index 1, text is empty in {'language': 'et', 'text': ''}"


def test_too_long_text_release_notes():
    argument_value = json.dumps(
        [
            {"language": "en-US", "text": "US notes"},
            {"language": "fi-FI", "text": "FI notes"},
            {"language": "et", "text": "0123456789 " * 50},
        ],
    )
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        ReleaseNotesArgument(argument_value)

    expected_error_prefix = (
        "Invalid release note on index 2, text is too long (exceeds 500 characters) in "
        "{'language': 'et', 'text': '0123456789 "
    )
    assert str(exc_info.value).startswith(expected_error_prefix)
