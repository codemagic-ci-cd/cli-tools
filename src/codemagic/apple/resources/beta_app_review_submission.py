from __future__ import annotations

from dataclasses import dataclass

from .resource import Relationship
from .resource import Resource


class BetaAppReviewSubmission(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betaappreviewsubmission
    """

    @dataclass
    class Relationships(Resource.Relationships):
        betaReviewState: Relationship
