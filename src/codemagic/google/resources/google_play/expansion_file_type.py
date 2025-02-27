from codemagic.models.enums import ResourceEnum


class ExpansionFileType(ResourceEnum):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/ExpansionFileType
    """

    UNSPECIFIED = "expansionFileTypeUnspecified"
    MAIN = "main"
    PATCH = "patch"
