import dataclasses

from codemagic.google.resources import Resource

from .language import Language


@dataclasses.dataclass
class LocalizedText(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#localizedtext
    """

    language: Language
    text: str = dataclasses.field(default="")

    def __post_init__(self):
        if isinstance(self.language, str):
            self.language = Language(self.language)
