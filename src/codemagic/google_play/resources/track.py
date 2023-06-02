from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import List
from typing import Optional

from .enums import ReleaseStatus
from .resource import Resource


@dataclass
class LocalizedText(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#localizedtext
    """

    language: str
    text: str


@dataclass
class CountryTargeting(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#countrytargeting
    """

    countries: List[str]
    includeRestOfWorld: Optional[bool] = None


@dataclass
class Release(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#release
    """

    _OMIT_IF_NONE_KEYS = (
        'name',
        'userFraction',
        'countryTargeting',
        'inAppUpdatePriority',
        'versionCodes',
        'releaseNotes',
    )

    status: ReleaseStatus
    name: Optional[str] = None
    userFraction: Optional[float] = None
    countryTargeting: Optional[CountryTargeting] = None
    inAppUpdatePriority: Optional[int] = None
    versionCodes: Optional[List[str]] = None
    releaseNotes: Optional[List[LocalizedText]] = None

    def __post_init__(self):
        if isinstance(self.releaseNotes, list):
            self.releaseNotes = [LocalizedText(**note) for note in self.releaseNotes]
        if isinstance(self.status, str):
            self.status = ReleaseStatus(self.status)
        if isinstance(self.countryTargeting, dict):
            self.countryTargeting = CountryTargeting(**self.countryTargeting)


@dataclass
class Track(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#Track
    """
    _OMIT_IF_NONE_KEYS = ('releases',)

    track: str
    releases: Optional[List[Release]] = None

    def __post_init__(self):
        if isinstance(self.releases, list):
            self.releases = [Release(**release) for release in self.releases]

    def get_max_version_code(self) -> int:
        error_prefix = f'Failed to get version code from "{self.track}" track'
        if not self.releases:
            raise ValueError(f'{error_prefix}: track has no releases')
        version_codes = [release.versionCodes for release in self.releases if release.versionCodes]
        if not version_codes:
            raise ValueError(f'{error_prefix}: releases with version code do not exist')
        return max(map(int, chain(*version_codes)))
