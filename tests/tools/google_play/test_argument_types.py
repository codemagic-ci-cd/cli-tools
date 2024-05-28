import pytest
from codemagic.tools.google_play.argument_types import CredentialsArgument


def test_valid_google_play_credentials():
    argument_value = r"""{
        "type": "service_account",
        "project_id": "project-id",
        "private_key_id": "private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "client_email": "codemagic@project-id.iam.gserviceaccount.com",
        "client_id": "client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/project-id.iam.gserviceaccount.com"
    }"""
    assert CredentialsArgument._is_valid(argument_value)


@pytest.mark.parametrize(
    "argument_value",
    (
        "{}",
        "1",
        '"lorem ipsum"',
        "[]",
        "[1, 2, 3]",
        '{"type": "private_key"}',
        "{",
        '"uncompleted string',
    ),
)
def test_invalid_google_play_credentials(argument_value: str):
    assert CredentialsArgument._is_valid(argument_value) is False
