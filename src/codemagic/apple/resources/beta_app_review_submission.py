from __future__ import annotations

from dataclasses import dataclass

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

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
