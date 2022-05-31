from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import Platform
from .enums import ReviewSubmissionState
from .resource import Relationship
from .resource import Resource


class ReviewSubmission(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/reviewsubmission
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        platform: Platform
        state: ReviewSubmissionState
        submittedDate: datetime

    @dataclass
    class Relationships(Resource.Relationships):
        items: Relationship
        app: Optional[Relationship] = None
        appStoreVersionForReview: Optional[Relationship] = None
