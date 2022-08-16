import pathlib
import shutil

import pytest

from codemagic.shell_tools import Keytool


@pytest.mark.skipif(not shutil.which('keytool'), reason='keytool is not available')
@pytest.mark.parametrize(
    'keystore_name, keystore_password, key_alias, expected_serial',
    [
        ('non-rfc-cert-keystore.jks', 'test123', 'debug', 1544133090),
        ('non-rfc-cert-keystore.p12', 'test123', 'debug', 1544133090),
        ('non-rfc-cert-keystore.jks', 'test123', 'codemagic', 63699888),
        ('non-rfc-cert-keystore.p12', 'test123', 'codemagic', 63699888),
        ('rfc-cert-keystore.jks', 'password', 'alias1', 14779024637510458532),
        ('rfc-cert-keystore.p12', 'password', 'alias1', 14779024637510458532),
        ('rfc-cert-keystore.jks', 'password', 'alias2', 3388580998731097051),
        ('rfc-cert-keystore.p12', 'password', 'alias2', 3388580998731097051),
        ('android.ks', 'password', 'alias', 6524856189795578914),
    ],
)
def test_get_certificate(keystore_name, keystore_password, key_alias, expected_serial):
    keystore_path = pathlib.Path(__file__).parent / 'mocks' / keystore_name
    certificate = Keytool().get_certificate(
        keystore_path=keystore_path,
        keystore_password=keystore_password,
        key_alias=key_alias,
    )
    assert certificate.serial == expected_serial
