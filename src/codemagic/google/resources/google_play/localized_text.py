import dataclasses

from codemagic.google.resources import Resource


@dataclasses.dataclass
class LocalizedText(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#localizedtext
    """

    language: str
    text: str
