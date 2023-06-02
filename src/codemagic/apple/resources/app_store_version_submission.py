from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resource import Relationship
from .resource import Resource


class AppStoreVersionSubmission(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/appstoreversionsubmission
    """

    attributes: Resource.Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Relationships(Resource.Relationships):
        appStoreVersion: Relationship
