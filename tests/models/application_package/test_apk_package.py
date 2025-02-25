import pathlib
from unittest import mock

import pytest

from codemagic.models.application_package import ApkPackage


@pytest.fixture
def certificate_der() -> bytes:
    mock_certificate_der_path = pathlib.Path(__file__).parent / "android" / "mocks" / "apk_certificate_x509.der"
    return mock_certificate_der_path.read_bytes()


@pytest.fixture
def mock_apk(certificate_der: bytes):
    with mock.patch("codemagic.models.application_package.apk_package.APK") as mock_apk_class:
        mock_apk = mock.MagicMock(
            get_signature_name=mock.MagicMock(return_value="META-INF/CERT.RSA"),
            get_certificate_der=mock.MagicMock(return_value=certificate_der),
        )
        mock_apk_class.return_value = mock_apk
        yield mock_apk


def test_certificate(mock_apk: mock.MagicMock):
    apk = ApkPackage("/path/to/app.apk")
    assert apk.certificate.subject == {"O": "Codemagic"}
    assert apk.certificate.serial == 1
