from __future__ import annotations

import dataclasses

from codemagic.google.resources import Resource


@dataclasses.dataclass
class Edit(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits
    """

    id: str
    expiryTimeSeconds: str
