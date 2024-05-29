import json

from codemagic import cli


class CredentialsArgument(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = "GCLOUD_SERVICE_ACCOUNT_CREDENTIALS"

    @classmethod
    def _is_valid(cls, value: str) -> bool:
        try:
            decoded = json.loads(value)
            return decoded["type"] == "service_account"
        except (ValueError, TypeError, KeyError):
            # ValueError - Call to json.loads fails
            # TypeError - Decoded object is not subscriptable, i.e. not a dictionary
            # KeyError - Key "type" is missing from decoded dictionary
            return False
