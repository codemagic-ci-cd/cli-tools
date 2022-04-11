import json

from codemagic import cli


class PackageName(str):
    pass


class CredentialsArgument(cli.EnvironmentArgumentValue[str]):
    environment_variable_key = 'GCLOUD_SERVICE_ACCOUNT_CREDENTIALS'

    @classmethod
    def _is_valid(cls, value: str) -> bool:
        try:
            json_content = json.loads(value)
        except json.decoder.JSONDecodeError:
            return False
        else:
            return json_content.get('type') == 'service_account'
