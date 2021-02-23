from __future__ import annotations

import json

from codemagic import cli


class GooglePlayTypes:
    class Credentials(str):
        pass

    class PackageName(str):
        pass

    class CredentialsArgument(cli.EnvironmentArgumentValue[Credentials]):
        environment_variable_key = 'GCLOUD_SERVICE_ACCOUNT_CREDENTIALS'

        @classmethod
        def _is_valid(cls, value: GooglePlayTypes.Credentials) -> bool:
            try:
                json_content = json.loads(value)
            except json.decoder.JSONDecodeError:
                return False
            else:
                return json_content.get('type') == 'service_account'
