import argparse
import json
from typing import Dict

from codemagic import cli


class CredentialsArgument(cli.EnvironmentArgumentValue[dict]):
    argument_type = dict
    environment_variable_key = 'FIREBASE_SERVICE_ACCOUNT_CREDENTIALS'

    @classmethod
    def _apply_type(cls, non_typed_value: str) -> Dict:
        try:
            return json.loads(non_typed_value)
        except json.decoder.JSONDecodeError as e:
            raise argparse.ArgumentTypeError(
                f'Provided value {non_typed_value!r} is not a valid JSON encoded object',
            ) from e

    @classmethod
    def _is_valid(cls, value) -> bool:
        return isinstance(value, dict) and value.get('type') == 'service_account'
