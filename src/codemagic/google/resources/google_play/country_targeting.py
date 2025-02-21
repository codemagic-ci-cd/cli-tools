import dataclasses
from typing import List
from typing import Optional

from codemagic.google.resources import Resource


@dataclasses.dataclass
class CountryTargeting(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#countrytargeting
    """

    countries: List[str]
    includeRestOfWorld: Optional[bool] = None
