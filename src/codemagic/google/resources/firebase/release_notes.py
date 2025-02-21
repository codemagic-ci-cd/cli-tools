from dataclasses import dataclass

from codemagic.google.resources import Resource


@dataclass
class ReleaseNotes(Resource):
    """
    https://firebase.google.com/docs/reference/app-distribution/rest/v1/projects.apps.releases#ReleaseNotes
    """

    text: str
