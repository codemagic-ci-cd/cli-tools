import dataclasses
from typing import Optional

from codemagic.google.resources import Resource


@dataclasses.dataclass
class ExpansionFile(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.expansionfiles
    """

    fileSize: Optional[str] = None
    referencesVersion: Optional[int] = None
