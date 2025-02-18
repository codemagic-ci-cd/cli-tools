import argparse
import json
from typing import Dict

from codemagic import cli


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
