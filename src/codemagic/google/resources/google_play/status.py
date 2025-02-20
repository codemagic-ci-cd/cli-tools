from codemagic.models.enums import ResourceEnum


class Status(ResourceEnum):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks#Status
    """

    STATUS_UNSPECIFIED = "statusUnspecified"
    DRAFT = "draft"
    IN_PROGRESS = "inProgress"
    HALTED = "halted"
    COMPLETED = "completed"
