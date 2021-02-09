from __future__ import annotations

from .resource import Resource


class ImageAsset(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/imageasset
    """

    templateUrl: str
    height: str
    width: str