import pathlib
import shutil
from tempfile import NamedTemporaryFile

import pytest

from codemagic.shell_tools import Keytool


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate(mock_keystore_path):
    valid = Keytool().validate_keystore(
        keystore_path=mock_keystore_path,
        key_alias='alias',
        keystore_password='password',
    )
    assert valid is True


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate_wrong_password(mock_keystore_path):
    with pytest.raises(ValueError) as exc_info:
        Keytool().validate_keystore(
            keystore_path=mock_keystore_path,
            key_alias='alias',
            keystore_password='wrong password',
        )
    assert str(exc_info.value) == 'Invalid keystore password'


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate_wrong_alias(mock_keystore_path):
    with pytest.raises(ValueError) as exc_info:
        Keytool().validate_keystore(
            keystore_path=mock_keystore_path,
            key_alias='wrong alias',
            keystore_password='password',
        )
    assert str(exc_info.value) == 'Alias "wrong alias" does not exist in keystore'


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate_invalid_path():
    with pytest.raises(ValueError) as exc_info:
        Keytool().validate_keystore(
            keystore_path=pathlib.Path('/keystore/does/not/exists.jks'),
            key_alias='alias',
            keystore_password='password',
        )
    assert str(exc_info.value) == 'Keystore does not exist'


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
def test_validate_certificate_invalid_keystore():
    with NamedTemporaryFile(prefix='keystore_', suffix='.jks', mode='wb') as tf:
        keystore_path = pathlib.Path(tf.name)
        tf.write(b'This is not a keystore')
        tf.flush()
        with pytest.raises(ValueError) as exc_info:
            Keytool().validate_keystore(
                keystore_path=keystore_path,
                key_alias='alias',
                keystore_password='password',
            )
    assert str(exc_info.value) == 'Unrecognized keystore format'
