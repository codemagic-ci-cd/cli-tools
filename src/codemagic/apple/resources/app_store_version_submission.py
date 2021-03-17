from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource


class AppStoreVersionSubmission(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/appstoreversionsubmission
    """

    @dataclass
    class Relationships(Resource.Relationships):
        appStoreVersion: Relationship
