from __future__ import annotations

from datetime import datetime
from datetime import timezone
from distutils.version import LooseVersion
from unittest import mock
from unittest.mock import PropertyMock

import cryptography
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from codemagic.models import Certificate
from codemagic.models import PrivateKey


@pytest.fixture
def certificate_signing_request_pem() -> bytes:
    return (
        b'-----BEGIN CERTIFICATE REQUEST-----\n'
        b'MIICUzCCATsCAQAwDjEMMAoGA1UEAwwDUEVNMIIBIjANBgkqhkiG9w0BAQEFAAOC\n'
        b'AQ8AMIIBCgKCAQEA0L+h5RVDhRpTjNttmXX5n0gNOVYTvSNPYRcNFlSISboQStDm\n'
        b'I65Ncv3Snsun7pzZfCSo+si/JFYw/C8hrwHTEmHS2AbK94w1oSYiQ1fiSKszmtc7\n'
        b'khw0vRUPJyzr+Ib8otXsdAgzpCoFYe6nQn3I/QWufLb3EOiul5R5yq6dMhhs0Fgc\n'
        b'y9hKA74ADk3TEk2cxz/9FyaNoc2MiQmkKX1WPWM74LVMKo0HXtp2xYZKVmX4hLaK\n'
        b'5w2fHP7qvm0wVTt5B3IJrgDEvg25/irYudIuy4T6gWOvhvUfJYDCqZ0N2kdGi3kQ\n'
        b'uguGTABIjdB54/9FN/ZyX3UL7fqRg9jG7P4i4QIDAQABoAAwDQYJKoZIhvcNAQEL\n'
        b'BQADggEBAAFhNwzZqthXp3NqGiCWARGTzV23bAIPAb3gT+usjw7KO4UgtQg/kerT\n'
        b'QflsOPX4i1wH+T2qTmYkXqvbrrxKtQaB/iKZgkuzDr6nZQROMDg9FOnMGmfoTjW7\n'
        b'jNCOCUyN3yMsN2SPD1HHVt3Yr0ZVtjC16hBiqhcFOsqdR4rPFul7frUaOFoDB+gX\n'
        b'jO1z5h+rKiWSm2cKPNi+d5YdsLZhpqeVTCzAdL6G44fmoyuEAcu9fpNoOvGJfGaG\n'
        b'eWxKc1lwqTa9JjSa/UUn/AHKRZBmEmCsA3j76um7bLEQmuGUeM8GxRFdjbt0vJak\n'
        b'NdSfE3CyTZIjFlFI/OXH9i1iqKI5DTE=\n'
        b'-----END CERTIFICATE REQUEST-----\n'
    )


@pytest.fixture
def certificate_pem() -> str:
    return (
        '-----BEGIN CERTIFICATE-----\n'
        'MIIC4DCCAcgCCQD4HAXNZV3lvTANBgkqhkiG9w0BAQsFADAyMQswCQYDVQQGEwJV\n'
        'SzEPMA0GA1UEBwwGTG9uZG9uMRIwEAYDVQQKDAlOZXZlcmNvZGUwHhcNMjEwMjIz\n'
        'MTIyMzI0WhcNMjIwMjIzMTIyMzI0WjAyMQswCQYDVQQGEwJVSzEPMA0GA1UEBwwG\n'
        'TG9uZG9uMRIwEAYDVQQKDAlOZXZlcmNvZGUwggEiMA0GCSqGSIb3DQEBAQUAA4IB\n'
        'DwAwggEKAoIBAQCtoOE48UvNuUxohAivQadfsebA9taurEqjrEUWFvonyss18yma\n'
        '54Y0i4ee0PDRvzbxaMUNEIC5bj2tlMhZ2NA+A+3Xs0W5aPtEeQoNAkf9qTOIWrev\n'
        'FuIolH0vD4wQCYjyFLVRCmNzS5CljnutU6DFqGzUGzHaEWRShEAEasntoykb4Llq\n'
        'kkgGAcT5vV88dyYhoA5HoofSSUhrfLP3AsGiw9OcDwhhRGMFwigLespIHpvFZVlY\n'
        '/+qxEKrXRTJQDpR1Q8CUVnQtvMK2NF05YjNd6mrqrVSjQaeOa0bBJJTIlJR9ZfCE\n'
        'EduCDhHs0KXDeHFusBoHULJeYUK4GwV/F8fvAgMBAAEwDQYJKoZIhvcNAQELBQAD\n'
        'ggEBAFHvSxSzRByoQSv4iMWd3s8vkWWE43tYzN5F3yNTpXfwj2lALA367lqyXBrK\n'
        'p7WSUJ1BQK4zJtcWVO5QcltrPqZeDUJcVh6ninxrqG7yICBMOwDXGuRd+TiQQV3g\n'
        'c30mFsfTnqV87oecob67p+2NlAv1AfR06c7DTMFSfqoPqs7b++WNxXX0nN+4GjZn\n'
        'hr2fa95WMFGUqWxVk7z7K+CQpcitPeTaoZfVHMAYQJRftKcjnuQJPy6kpaPrV2t3\n'
        'BK6onwVPmrXNMcCuW8feeYf1Hbuaymk6K0ED3PwJBMW+GNehslHZTHGPZABd6Zl/\n'
        '5DlU4cIG1Rtk9jAEDPceRFfBZP4=\n'
        '-----END CERTIFICATE-----\n'
    )


@pytest.fixture
def private_key_pem() -> str:
    return (
        '-----BEGIN RSA PRIVATE KEY-----\n'
        'MIIEowIBAAKCAQEAraDhOPFLzblMaIQIr0GnX7HmwPbWrqxKo6xFFhb6J8rLNfMp\n'
        'mueGNIuHntDw0b828WjFDRCAuW49rZTIWdjQPgPt17NFuWj7RHkKDQJH/akziFq3\n'
        'rxbiKJR9Lw+MEAmI8hS1UQpjc0uQpY57rVOgxahs1Bsx2hFkUoRABGrJ7aMpG+C5\n'
        'apJIBgHE+b1fPHcmIaAOR6KH0klIa3yz9wLBosPTnA8IYURjBcIoC3rKSB6bxWVZ\n'
        'WP/qsRCq10UyUA6UdUPAlFZ0LbzCtjRdOWIzXepq6q1Uo0GnjmtGwSSUyJSUfWXw\n'
        'hBHbgg4R7NClw3hxbrAaB1CyXmFCuBsFfxfH7wIDAQABAoIBAH/qGEM1MZ18OBh/\n'
        'vU4wVjif/dqHf53r/Ikcb0FY6C7Mrm0umaYvj6XCbcXJNMGx165+ez2mvM7fsrzg\n'
        '8cGPg8tMZbsVrfZsq0DE02zGE3eDYh3Ah7aMa01uJ9O15oAiJiwCqZnsx1u3ffca\n'
        'Q29sPvOfo52X82Auk/RezjLy4ZUZ+pacv8+JlvMajQeJaXIvHoqNBEn2N6CHg6fT\n'
        'ar9f7OQm4yQKyp0XqoOEKcGrdcRCCX+rpEyi/trBnIkKEgrsqhD0JtsFeZzR5Akc\n'
        '6a+ZOJtFz3ZRWLSjAlXKNeU2ZIJGsvzj7L6SvNyM+yc5vgnilTc6WUD2Lkj6tQMA\n'
        'D9q6g2ECgYEA1ALChJJrSJHOQG2s/AKzUU3cwtktDKz2OqOeWAcCy9ClTcKs8Ur2\n'
        'phKmJ3rwuxe984dOyie/rOdC0U4RZZQFSuhEHFrpAxRNrAvNH+BYIrPAm7NHN9SO\n'
        'HPyq/KTZiU1wFAZqFy+PYXF4MO9/Aw2+nyuMXRZj76Dqk729xVDZ+NcCgYEA0adj\n'
        'whqEg+NelNXAXKHCTOxjeBo8gYaSLj6D4TARXwa6ibxsScFh5imcu4KGRBXFsmcv\n'
        'Qc+T7wfuv41Ctt+nEH2fAULEqMq7IL68x+QhyTW5pKZZGyyoU8smUNY1Fa3LEYjh\n'
        'Dbv39zCBZI6Keph0W137R6OnYV1Z2aw3CeSHTqkCgYA2hbcsjNMWSJj4LLxt2uvu\n'
        'ns2FNoDFX726+tT/4l2vuKqqQsRjEVo4/1bHlHBQTRzGgiebCXnbp2WhmigTLWvn\n'
        'BbBuclq2NgR7mFVaO0GvOvbvk71e+ETL45a9fk+LZeTK4ZNq/woqjxnPy+eoC2LY\n'
        'YESqs9VjjMiG0ib5lX9Y5QKBgAR4EftQP2TkUt7PU6Nl21Nycohb3tBQAwuzT3Jc\n'
        'aPJinVVUS+ailainWGzy0lPfNvCfnHVFrHya6a7xnutxBwml896+Ap0qfSSsjC+i\n'
        'oEm+uG9XEG0w3YGzweRVPJpysvJzvYBicl21jfyLwU3ttAVCkpmrVmUP7VtjfWTb\n'
        'lzrJAoGBAK/ShYyeqoUEWhXHKmIB160TBVMsyJ8R8equLdsRLvCDylrCnEMVelx0\n'
        'YzyAuISQlvMR6jIFDFVhiC0Cq0kbXKHvtR0yBU0U7P9O943DnPkepsd2t4O0NbE3\n'
        'r68Y2YN1FWfNkxbZR/LA431G1JWilaNcSHY4k4wSMpd4l9q+Pbvd\n'
        '-----END RSA PRIVATE KEY-----\n'
    )


@pytest.fixture
def certificate(certificate_asn1) -> Certificate:
    return Certificate.from_ans1(certificate_asn1)


@pytest.mark.skipif(
    LooseVersion(cryptography.__version__) < LooseVersion('36.0.0'),
    reason=(
        f'Cryptography {cryptography.__version__} < 36.0.0 generates '
        f'slightly different CSR public bytes for certificate request '
        f'than is expected here.'
    ),
)
def test_create_certificate_signing_request(unencrypted_pem, certificate_signing_request_pem):
    pk = PrivateKey.from_pem(unencrypted_pem.content)
    csr = Certificate.create_certificate_signing_request(pk)
    assert csr.signature_hash_algorithm.name == 'sha256'
    assert csr.is_signature_valid is True
    assert csr.public_bytes(serialization.Encoding.PEM) == certificate_signing_request_pem


def test_certificate_has_key(certificate, unencrypted_pem):
    pk = PrivateKey.from_pem(unencrypted_pem.content)
    assert certificate.is_signed_with(pk) is True


def test_certificate_does_not_have_key(certificate, encrypted_pem):
    pk = PrivateKey.from_pem(encrypted_pem.content, encrypted_pem.password)
    assert certificate.is_signed_with(pk) is False


def test_p12_to_certificate(mock_certificate_p12, certificate_pem, private_key_pem):
    p12_bytes = mock_certificate_p12.read_bytes()

    certificate = Certificate.from_p12(p12_bytes, '123456')

    assert certificate.is_signed_with(PrivateKey.from_pem(private_key_pem))
    assert certificate.as_pem() == certificate_pem
    assert certificate.serial == 17878171000481113533
    assert certificate.issuer == {'C': 'UK', 'L': 'London', 'O': 'Nevercode'}


def test_p12_to_certificate_no_password(mock_certificate_p12_no_password):
    p12_bytes = mock_certificate_p12_no_password.read_bytes()

    certificate = Certificate.from_p12(p12_bytes)
    assert certificate.serial == 17878171000481113533


@pytest.mark.parametrize('cert_common_name, is_code_signing_certificate', [
    ('Apple Development: Some name (FXZPHT7PIC)', True),
    ('Apple Distribution: Some name (FXZPHT7PIC)', True),
    ('iPhone Developer: Some name (FXZPHT7PIC)', True),
    ('iPhone Distribution: Some name (FXZPHT7PIC)', True),
    ('Developer ID Application: Some name (FXZPHT7PIC)', True),
    ('Mac Developer: Some name (FXZPHT7PIC)', True),
    ('3rd Party Mac Developer Application: Some name (FXZPHT7PIC)', True),
    ('3rd Party Mac Developer Installer: Some name (FXZPHT7PIC)', True),
    ('iPhone Development: Some name (FXZPHT7PIC)', False),
    ('Apple Worldwide Developer Relations Certification Authority', False),
])
def test_is_code_signing_certificate(cert_common_name, is_code_signing_certificate, certificate):
    patched_common_name = mock.PropertyMock(return_value=cert_common_name)
    with mock.patch.object(Certificate, 'common_name', new_callable=patched_common_name):
        assert certificate.is_code_signing_certificate() is is_code_signing_certificate


def test_certificate_sha1_fingerprint(certificate):
    expected_fingerprint = 'F9 DA F0 C5 BA 5C 82 1E 46 25 D8 C4 3E 69 66 CF 8F 63 86 37'
    assert certificate.get_fingerprint(hashes.SHA1()) == expected_fingerprint.replace(' ', '')


def test_certificate_sha256_fingerprint(certificate):
    expected_fingerprint = \
        '42 FD E9 13 4E 92 B3 FC 2C 60 47 A9 6F B3 31 38 8F B4 60 85 BC B3 7C 67 0F 5D 78 76 1F DE E5 E3'
    assert certificate.get_fingerprint(hashes.SHA256()) == expected_fingerprint.replace(' ', '')


@pytest.mark.parametrize('is_development_cert, cert_common_name', [
    (False, '3rd Party Mac Developer Application: NEVERCODE LTD (X8NNQ9CYL2)'),
    (False, '3rd Party Mac Developer Installer: NEVERCODE LTD (X8NNQ9CYL2)'),
    (False, 'Apple Distribution: NEVERCODE LTD (X8NNQ9CYL2)'),
    (False, 'Developer ID Application: NEVERCODE LTD (X8NNQ9CYL2)'),
    (False, 'iPhone Distribution: NEVERCODE LTD (X8NNQ9CYL2)'),
    (True, 'Apple Development: NEVERCODE LTD (X8NNQ9CYL2)'),
    (True, 'Mac Developer: Created via API (83G8YPW74M)'),
    (True, 'iPhone Developer: Created via API (83G8YPW74M)'),
])
def test_is_development_certificate(is_development_cert, cert_common_name, certificate):
    patched_common_name = PropertyMock(return_value=cert_common_name)
    with mock.patch.object(Certificate, 'common_name', new_callable=patched_common_name):
        assert certificate.is_development_certificate is is_development_cert


def test_subject(certificate):
    expected_subject = {
        'C': 'US',
        'CN': 'iPhone Developer: Created via API (6HQ443353U)',
        'O': 'NEVERCODE LTD',
        'OU': 'X8NNQ9CYL2',
        'UID': '6HQ443353U',
    }
    assert certificate.subject == expected_subject


def test_issuer(certificate):
    expected_issuer = {
        'C': 'US',
        'CN': 'Apple Worldwide Developer Relations Certification Authority',
        'O': 'Apple Inc.',
        'OU': 'Apple Worldwide Developer Relations',
    }
    assert certificate.issuer == expected_issuer


def test_not_before(certificate):
    assert certificate.not_before == '20191129113745Z'


def test_not_after(certificate):
    assert certificate.not_after == '20201128113745Z'


def test_expires_at(certificate):
    expected_expires_at = datetime(2020, 11, 28, 11, 37, 45, tzinfo=timezone.utc)
    assert certificate.expires_at == expected_expires_at


def test_has_expired(certificate):
    assert certificate.has_expired is True


def test_serial(certificate):
    assert certificate.serial == 5308349992945343936


def test_extensions(certificate):
    expected_extensions = [
        'Unknown OID',
        'authorityInfoAccess',
        'authorityKeyIdentifier',
        'basicConstraints',
        'certificatePolicies',
        'extendedKeyUsage',
        'keyUsage',
        'subjectKeyIdentifier',
    ]
    assert sorted(certificate.extensions) == expected_extensions
