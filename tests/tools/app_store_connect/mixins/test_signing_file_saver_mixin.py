from __future__ import annotations

import logging
import pathlib
from unittest import mock

from codemagic.tools.app_store_connect.mixins import SigningFileSaverMixin
from codemagic.tools.app_store_connect.resource_printer import ResourcePrinter


class _SigningFileSaver(SigningFileSaverMixin):
    def __init__(self, profiles_directory: pathlib.Path):
        self.profiles_directory = profiles_directory
        self.printer = ResourcePrinter(False, mock.Mock())


def test_save_profiles_skips_profile_without_content(tmp_path, caplog, profile, profile_without_content):
    saver = _SigningFileSaver(tmp_path)

    with caplog.at_level(logging.WARNING):
        saved_paths = saver._save_profiles([profile_without_content, profile])

    assert len(saved_paths) == 1
    assert saved_paths[0].read_bytes() == profile.profile_content
    assert list(tmp_path.iterdir()) == saved_paths
    assert "profile content is missing" in caplog.text
