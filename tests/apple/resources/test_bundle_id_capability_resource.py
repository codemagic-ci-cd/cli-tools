from __future__ import annotations

import json
import pathlib
from typing import Dict

import pytest

from codemagic_cli_tools.apple.resources import BundleIdCapability


def test_bundle_id_capability_initialization(api_bundle_id_capability):
    bundle_id_capability = BundleIdCapability(api_bundle_id_capability)
    assert bundle_id_capability.dict() == api_bundle_id_capability
