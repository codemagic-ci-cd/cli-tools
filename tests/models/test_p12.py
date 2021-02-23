from pathlib import Path

from codemagic.models import Certificate
from codemagic.models import PrivateKey

certificate_bytes = \
    '-----BEGIN CERTIFICATE-----\n' \
    'MIIC4DCCAcgCCQD4HAXNZV3lvTANBgkqhkiG9w0BAQsFADAyMQswCQYDVQQGEwJV\n' \
    'SzEPMA0GA1UEBwwGTG9uZG9uMRIwEAYDVQQKDAlOZXZlcmNvZGUwHhcNMjEwMjIz\n' \
    'MTIyMzI0WhcNMjIwMjIzMTIyMzI0WjAyMQswCQYDVQQGEwJVSzEPMA0GA1UEBwwG\n' \
    'TG9uZG9uMRIwEAYDVQQKDAlOZXZlcmNvZGUwggEiMA0GCSqGSIb3DQEBAQUAA4IB\n' \
    'DwAwggEKAoIBAQCtoOE48UvNuUxohAivQadfsebA9taurEqjrEUWFvonyss18yma\n' \
    '54Y0i4ee0PDRvzbxaMUNEIC5bj2tlMhZ2NA+A+3Xs0W5aPtEeQoNAkf9qTOIWrev\n' \
    'FuIolH0vD4wQCYjyFLVRCmNzS5CljnutU6DFqGzUGzHaEWRShEAEasntoykb4Llq\n' \
    'kkgGAcT5vV88dyYhoA5HoofSSUhrfLP3AsGiw9OcDwhhRGMFwigLespIHpvFZVlY\n' \
    '/+qxEKrXRTJQDpR1Q8CUVnQtvMK2NF05YjNd6mrqrVSjQaeOa0bBJJTIlJR9ZfCE\n' \
    'EduCDhHs0KXDeHFusBoHULJeYUK4GwV/F8fvAgMBAAEwDQYJKoZIhvcNAQELBQAD\n' \
    'ggEBAFHvSxSzRByoQSv4iMWd3s8vkWWE43tYzN5F3yNTpXfwj2lALA367lqyXBrK\n' \
    'p7WSUJ1BQK4zJtcWVO5QcltrPqZeDUJcVh6ninxrqG7yICBMOwDXGuRd+TiQQV3g\n' \
    'c30mFsfTnqV87oecob67p+2NlAv1AfR06c7DTMFSfqoPqs7b++WNxXX0nN+4GjZn\n' \
    'hr2fa95WMFGUqWxVk7z7K+CQpcitPeTaoZfVHMAYQJRftKcjnuQJPy6kpaPrV2t3\n' \
    'BK6onwVPmrXNMcCuW8feeYf1Hbuaymk6K0ED3PwJBMW+GNehslHZTHGPZABd6Zl/\n' \
    '5DlU4cIG1Rtk9jAEDPceRFfBZP4=\n' \
    '-----END CERTIFICATE-----\n'

signing_certificate = \
    '-----BEGIN RSA PRIVATE KEY-----\n' \
    'MIIEowIBAAKCAQEAraDhOPFLzblMaIQIr0GnX7HmwPbWrqxKo6xFFhb6J8rLNfMp\n' \
    'mueGNIuHntDw0b828WjFDRCAuW49rZTIWdjQPgPt17NFuWj7RHkKDQJH/akziFq3\n' \
    'rxbiKJR9Lw+MEAmI8hS1UQpjc0uQpY57rVOgxahs1Bsx2hFkUoRABGrJ7aMpG+C5\n' \
    'apJIBgHE+b1fPHcmIaAOR6KH0klIa3yz9wLBosPTnA8IYURjBcIoC3rKSB6bxWVZ\n' \
    'WP/qsRCq10UyUA6UdUPAlFZ0LbzCtjRdOWIzXepq6q1Uo0GnjmtGwSSUyJSUfWXw\n' \
    'hBHbgg4R7NClw3hxbrAaB1CyXmFCuBsFfxfH7wIDAQABAoIBAH/qGEM1MZ18OBh/\n' \
    'vU4wVjif/dqHf53r/Ikcb0FY6C7Mrm0umaYvj6XCbcXJNMGx165+ez2mvM7fsrzg\n' \
    '8cGPg8tMZbsVrfZsq0DE02zGE3eDYh3Ah7aMa01uJ9O15oAiJiwCqZnsx1u3ffca\n' \
    'Q29sPvOfo52X82Auk/RezjLy4ZUZ+pacv8+JlvMajQeJaXIvHoqNBEn2N6CHg6fT\n' \
    'ar9f7OQm4yQKyp0XqoOEKcGrdcRCCX+rpEyi/trBnIkKEgrsqhD0JtsFeZzR5Akc\n' \
    '6a+ZOJtFz3ZRWLSjAlXKNeU2ZIJGsvzj7L6SvNyM+yc5vgnilTc6WUD2Lkj6tQMA\n' \
    'D9q6g2ECgYEA1ALChJJrSJHOQG2s/AKzUU3cwtktDKz2OqOeWAcCy9ClTcKs8Ur2\n' \
    'phKmJ3rwuxe984dOyie/rOdC0U4RZZQFSuhEHFrpAxRNrAvNH+BYIrPAm7NHN9SO\n' \
    'HPyq/KTZiU1wFAZqFy+PYXF4MO9/Aw2+nyuMXRZj76Dqk729xVDZ+NcCgYEA0adj\n' \
    'whqEg+NelNXAXKHCTOxjeBo8gYaSLj6D4TARXwa6ibxsScFh5imcu4KGRBXFsmcv\n' \
    'Qc+T7wfuv41Ctt+nEH2fAULEqMq7IL68x+QhyTW5pKZZGyyoU8smUNY1Fa3LEYjh\n' \
    'Dbv39zCBZI6Keph0W137R6OnYV1Z2aw3CeSHTqkCgYA2hbcsjNMWSJj4LLxt2uvu\n' \
    'ns2FNoDFX726+tT/4l2vuKqqQsRjEVo4/1bHlHBQTRzGgiebCXnbp2WhmigTLWvn\n' \
    'BbBuclq2NgR7mFVaO0GvOvbvk71e+ETL45a9fk+LZeTK4ZNq/woqjxnPy+eoC2LY\n' \
    'YESqs9VjjMiG0ib5lX9Y5QKBgAR4EftQP2TkUt7PU6Nl21Nycohb3tBQAwuzT3Jc\n' \
    'aPJinVVUS+ailainWGzy0lPfNvCfnHVFrHya6a7xnutxBwml896+Ap0qfSSsjC+i\n' \
    'oEm+uG9XEG0w3YGzweRVPJpysvJzvYBicl21jfyLwU3ttAVCkpmrVmUP7VtjfWTb\n' \
    'lzrJAoGBAK/ShYyeqoUEWhXHKmIB160TBVMsyJ8R8equLdsRLvCDylrCnEMVelx0\n' \
    'YzyAuISQlvMR6jIFDFVhiC0Cq0kbXKHvtR0yBU0U7P9O943DnPkepsd2t4O0NbE3\n' \
    'r68Y2YN1FWfNkxbZR/LA431G1JWilaNcSHY4k4wSMpd4l9q+Pbvd\n' \
    '-----END RSA PRIVATE KEY-----\n'


def test_p12_to_certificate():
    p12_path = Path(__file__).parent / 'certificate.p12'
    p12_bytes = p12_path.read_bytes()

    certificate = Certificate.from_p12(p12_bytes, '123456')

    certificate.is_signed_with(PrivateKey.from_pem(signing_certificate))
    assert certificate.as_pem() == certificate_bytes
    assert certificate.serial == 17878171000481113533
    assert certificate.issuer == {'C': 'UK', 'L': 'London', 'O': 'Nevercode'}


def test_p12_to_certificate_no_password():
    p12_path = Path(__file__).parent / 'certificate-no-password.p12'
    p12_bytes = p12_path.read_bytes()

    certificate = Certificate.from_p12(p12_bytes)
    assert certificate.serial == 17878171000481113533
