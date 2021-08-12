from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import BetaReviewState
from .resource import Relationship
from .resource import Resource


class BetaAppReviewSubmission(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betaappreviewsubmission
    """

    @dataclass
    class Attributes(Resource.Attributes):
        betaReviewState: BetaReviewState
        submittedDate: Optional[datetime]

        def __post_init__(self):
            if isinstance(self.betaReviewState, str):
                self.betaReviewState = BetaReviewState(self.betaReviewState)

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
