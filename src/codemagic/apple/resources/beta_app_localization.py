from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import Locale
from .resource import Relationship
from .resource import Resource


class BetaAppLocalization(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/betaapplocalization
    """

    @dataclass
    class Attributes(Resource.Attributes):
        description: Optional[str]
        feedbackEmail: Optional[str]
        locale: Locale
        marketingUrl: Optional[str]
        privacyPolicyUrl: Optional[str]
        tvOsPrivacyPolicy: Optional[str]

    @dataclass
    class Relationships(Resource.Relationships):
        app: Relationship
