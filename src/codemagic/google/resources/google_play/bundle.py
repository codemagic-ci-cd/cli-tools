import dataclasses

from codemagic.google.resources import Resource


@dataclasses.dataclass
class Bundle(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.bundles#resource:-bundle
    """

    versionCode: int
    sha1: str
    sha256: str
