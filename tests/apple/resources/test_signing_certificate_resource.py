from __future__ import annotations

from codemagic.apple.resources import SigningCertificate


def test_signing_certificate_initialization(api_certificate):
    certificate = SigningCertificate(api_certificate)
    assert certificate.dict() == api_certificate
