import argparse
import json
from typing import Dict

from codemagic import cli
from codemagic.google.resources.firebase import OrderBy
from codemagic.models.enums import ResourceEnum


class ReleasesOrderByArgument(ResourceEnum):
    CREATE_TIME_DESC = "createTimeDesc"
    CREATE_TIME_ASC = "createTime"

    @property
    def order_by(self) -> OrderBy:
        return OrderBy[self.name]


class CredentialsArgument(cli.EnvironmentArgumentValue[dict]):
    argument_type = dict
    environment_variable_key = "FIREBASE_SERVICE_ACCOUNT_CREDENTIALS"

    def _apply_type(self, non_typed_value: str) -> Dict[str, str]:
        try:
            value = json.loads(non_typed_value)
        except json.decoder.JSONDecodeError as e:
            raise argparse.ArgumentTypeError("Provided value is not a valid JSON") from e

        if isinstance(value, dict) and value.get("type") == "service_account":
            return value
        raise argparse.ArgumentTypeError("Provided value is not a service account object")
