from __future__ import annotations

import dataclasses
from itertools import chain
from typing import List
from typing import Optional

from codemagic.google.resources import Resource

from .release import Release


@dataclasses.dataclass
class Track(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#Track
    """

    _OMIT_IF_NONE_KEYS = ("releases",)

    track: str
    releases: Optional[List[Release]] = None

    def __post_init__(self):
        if isinstance(self.releases, list):
            self.releases = [self._typed_release(release) for release in self.releases]

    @classmethod
    def _typed_release(cls, release: Release | dict) -> Release:
        if isinstance(release, Release):
            return release
        elif isinstance(release, dict):
            return Release(**release)
        else:
            raise ValueError(f"Unsupported release type: {type(release)}")

    def get_max_version_code(self) -> int:
        # TODO: Remove business logic from model
        error_prefix = f'Failed to get version code from "{self.track}" track'
        if not self.releases:
            raise ValueError(f"{error_prefix}: track has no releases")
        version_codes = [release.versionCodes for release in self.releases if release.versionCodes]
        if not version_codes:
            raise ValueError(f"{error_prefix}: releases with version code do not exist")
        return max(map(int, chain(*version_codes)))
