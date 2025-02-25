import dataclasses
from typing import Optional

from codemagic.google.resources import Resource


@dataclasses.dataclass
class InternalAppSharingArtifact(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/internalappsharingartifacts#resource:-internalappsharingartifact
    """

    downloadUrl: Optional[str] = None
    certificateFingerprint: Optional[str] = None
    sha256: Optional[str] = None
