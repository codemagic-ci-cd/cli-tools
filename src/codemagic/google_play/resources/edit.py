from __future__ import annotations

from dataclasses import dataclass

from .resource import Resource


@dataclass
class Edit(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits
    """

    id: str
    expiryTimeSeconds: str
