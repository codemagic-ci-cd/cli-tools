import dataclasses

from codemagic.google.resources import Resource

from .apk_binary import ApkBinary


@dataclasses.dataclass
class Apk(Resource):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.apks#resource:-apk
    """

    versionCode: int
    binary: ApkBinary
