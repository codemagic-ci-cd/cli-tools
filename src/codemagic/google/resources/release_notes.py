from dataclasses import dataclass

from .resource import Resource


@dataclass
class ReleaseNotes(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#ReleaseNotes
    """

    text: str
