import shutil

import pytest

from codemagic.shell_tools import Keytool


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_get_certificates(mock_keystore_path):
    certificates = Keytool().get_certificates(
        keystore_path=mock_keystore_path,
        keystore_password='password',
    )
    assert len(certificates) == 1
    certificate = certificates[0]
    assert certificate.serial == 6524856189795578914


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_get_certificates_with_alias(mock_keystore_path):
    certificates = Keytool().get_certificates(
        keystore_path=mock_keystore_path,
        keystore_password='password',
        key_alias='alias',
    )
    assert len(certificates) == 1
    certificate = certificates[0]
    assert certificate.serial == 6524856189795578914


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_get_certificate_invalid_alias(mock_keystore_path):
    with pytest.raises(ValueError) as exc_info:
        Keytool().get_certificates(
            keystore_path=mock_keystore_path,
            key_alias='wrong alias',
            keystore_password='password',
        )
    assert str(exc_info.value) == 'Alias "wrong alias" does not exist in keystore'


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate_wrong_password(mock_keystore_path):
    with pytest.raises(ValueError) as exc_info:
        Keytool().get_certificates(
            keystore_path=mock_keystore_path,
            key_alias='alias',
            keystore_password='wrong password',
        )
    assert str(exc_info.value) == 'Invalid keystore password'
