import dataclasses

from codemagic.google.resources import Resource


@dataclasses.dataclass
class ApkBinary(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.apks#apkbinary
    """

    sha1: str
    sha256: str
