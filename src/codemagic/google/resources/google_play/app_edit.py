from __future__ import annotations

import dataclasses

from codemagic.google.resources import Resource


@dataclasses.dataclass
class AppEdit(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits#resource:-appedit
    """

    id: str
    expiryTimeSeconds: str
