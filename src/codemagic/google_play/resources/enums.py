from codemagic.models.enums import ResourceEnum


class ReleaseStatus(ResourceEnum):
    STATUS_UNSPECIFIED = 'statusUnspecified'
    DRAFT = 'draft'
    IN_PROGRESS = 'inProgress'
    HALTED = 'halted'
    COMPLETED = 'completed'
