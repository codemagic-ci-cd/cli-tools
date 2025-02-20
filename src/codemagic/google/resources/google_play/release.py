import dataclasses
from typing import List
from typing import Optional
from typing import Union

from codemagic.google.resources import Resource

from .country_targeting import CountryTargeting
from .localized_text import LocalizedText
from .status import Status


@dataclasses.dataclass
class Release(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#release
    """

    _OMIT_IF_NONE_KEYS = (
        "name",
        "userFraction",
        "countryTargeting",
        "inAppUpdatePriority",
        "versionCodes",
        "releaseNotes",
    )

    status: Status
    name: Optional[str] = None
    userFraction: Optional[float] = None
    countryTargeting: Optional[CountryTargeting] = None
    inAppUpdatePriority: Optional[int] = None
    versionCodes: Optional[List[str]] = None
    releaseNotes: Optional[List[LocalizedText]] = None

    def __post_init__(self):
        if isinstance(self.releaseNotes, list):
            self.releaseNotes = [self._typed_note(note) for note in self.releaseNotes]
        if isinstance(self.status, str):
            self.status = Status(self.status)
        if isinstance(self.countryTargeting, dict):
            self.countryTargeting = CountryTargeting(**self.countryTargeting)

    @classmethod
    def _typed_note(cls, note: Union[LocalizedText, dict]) -> LocalizedText:
        if isinstance(note, LocalizedText):
            return note
        elif isinstance(note, dict):
            return LocalizedText(**note)
        else:
            raise ValueError(f"Unsupported note type: {type(note)}")
