from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import ReviewSubmissionItemState
from .resource import Relationship
from .resource import Resource


class ReviewSubmissionItem(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/reviewsubmissionitem
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        state: ReviewSubmissionItemState

    @dataclass
    class Relationships(Resource.Relationships):
        appCustomProductPageVersion: Optional[Relationship] = None
        appEvent: Optional[Relationship] = None
        appStoreVersion: Optional[Relationship] = None
        appStoreVersionExperiment: Optional[Relationship] = None
