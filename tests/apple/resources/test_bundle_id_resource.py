from __future__ import annotations

import pytest

from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import Profile


def test_bundle_id_initialization(api_bundle_id):
    bundle_id = BundleId(api_bundle_id)
    assert bundle_id.dict() == api_bundle_id
