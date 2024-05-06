from __future__ import annotations

from datetime import datetime
from datetime import timezone

from codemagic.apple.resources import AppStoreVersionPhasedRelease
from codemagic.apple.resources import PhasedReleaseState
from codemagic.apple.resources.resource import ResourceLinks


def test_app_store_version_phased_release_initialization(api_app_store_version_phased_release):
    app_store_version_phased_release = AppStoreVersionPhasedRelease(api_app_store_version_phased_release)

    attributes: AppStoreVersionPhasedRelease.Attributes = app_store_version_phased_release.attributes
    assert attributes.phasedReleaseState is PhasedReleaseState.ACTIVE
    assert attributes.startDate == datetime(year=2024, month=4, day=24, hour=12, tzinfo=timezone.utc)
    assert attributes.totalPauseDuration == 3
    assert attributes.currentDayNumber == 1

    assert app_store_version_phased_release.relationships is None

    url = "https://api.appstoreconnect.apple.com/v1/appStoreVersionPhasedReleases/409ebefb-ebd1-4f1a-903d-6ba16e013ebf"
    assert app_store_version_phased_release.links == ResourceLinks(self=url)


def test_app_store_version_phased_release_dist_serialization(api_app_store_version_phased_release):
    app_store_version_phased_release = AppStoreVersionPhasedRelease(api_app_store_version_phased_release)
    assert app_store_version_phased_release.dict() == api_app_store_version_phased_release
