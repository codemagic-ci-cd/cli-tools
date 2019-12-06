from __future__ import annotations

from codemagic_cli_tools.apple.resources import Certificate


def test_certificate_initialization(api_certificate):
    certificate = Certificate(api_certificate)
    assert certificate.dict() == api_certificate
