from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import ExternalBetaState
from .enums import InternalBetaState
from .resource import Relationship
from .resource import Resource


class BuildBetaDetail(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/buildbetadetail
    """

    attributes: Attributes
    relationships: Optional[Relationships] = None

    @dataclass
    class Attributes(Resource.Attributes):
        autoNotifyEnabled: bool
        externalBuildState: ExternalBetaState
        internalBuildState: InternalBetaState

        def __post_init__(self):
            if isinstance(self.externalBuildState, str):
                self.externalBuildState = ExternalBetaState(self.externalBuildState)
            if isinstance(self.internalBuildState, str):
                self.internalBuildState = InternalBetaState(self.internalBuildState)

    @dataclass
    class Relationships(Resource.Relationships):
        build: Relationship
