import argparse
import json
from collections import Counter
from typing import Dict
from typing import List

from codemagic import cli
from codemagic.google.resources.google_play import Language
from codemagic.google.resources.google_play import LocalizedText


class CredentialsArgument(cli.EnvironmentArgumentValue[dict]):
    environment_variable_key = "GOOGLE_PLAY_SERVICE_ACCOUNT_CREDENTIALS"
    deprecated_environment_variable_key = "GCLOUD_SERVICE_ACCOUNT_CREDENTIALS"

    def _apply_type(self, non_typed_value: str) -> Dict[str, str]:
        try:
            value = json.loads(non_typed_value)
        except json.decoder.JSONDecodeError as e:
            raise argparse.ArgumentTypeError("Provided value is not a valid JSON") from e

        if isinstance(value, dict) and value.get("type") == "service_account":
            return value
        raise argparse.ArgumentTypeError("Provided value is not a service account object")


class ReleaseNotesArgument(cli.EnvironmentArgumentValue[List[LocalizedText]]):
    argument_type = List[LocalizedText]
    environment_variable_key = "GOOGLE_PLAY_RELEASE_NOTES"
    example_value = json.dumps([{"language": "en-US", "text": "What's new in English"}])

    def _apply_type(self, non_typed_value: str) -> List[LocalizedText]:
        try:
            given_release_notes = json.loads(non_typed_value)
            if not isinstance(given_release_notes, list):
                raise ValueError("Not a list")
        except ValueError:
            raise argparse.ArgumentTypeError(f"Provided value {non_typed_value!r} is not a valid JSON encoded list")

        release_notes: List[LocalizedText] = []
        error_prefix = "Invalid release note"
        for i, rn in enumerate(given_release_notes):
            try:
                language = Language(rn["language"])
                text = rn["text"]
                if not isinstance(text, str):
                    raise ValueError("text is not a string")
                if len(text) > 500:
                    raise ValueError("text is too long (exceeds 500 characters)")
            except TypeError:  # Given beta build localization is not a dictionary
                raise argparse.ArgumentTypeError(f"{error_prefix} value {rn!r} on index {i}")
            except ValueError as ve:  # Invalid language or text
                raise argparse.ArgumentTypeError(f"{error_prefix} on index {i}, {ve} in {rn!r}")
            except KeyError as ke:  # Required key is missing from input
                raise argparse.ArgumentTypeError(f"{error_prefix} on index {i}, missing {ke.args[0]} in {rn!r}")
            release_notes.append(LocalizedText(language=language, text=text))

        languages = Counter(rn.language for rn in release_notes)
        if duplicate_locales := {language.value for language, uses in languages.items() if language and uses > 1}:
            raise argparse.ArgumentTypeError(
                (
                    f"Ambiguous definitions for language(s) {', '.join(duplicate_locales)}. "
                    "Please define release notes for each language exactly once."
                ),
            )

        return release_notes
