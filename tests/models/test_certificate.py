from __future__ import annotations

import pytest

from models import Certificate


@pytest.mark.skip(reason='Test not ready')
def test_create_certificate_signing_request():
    # TODO
    Certificate.create_certificate_signing_request(...)
