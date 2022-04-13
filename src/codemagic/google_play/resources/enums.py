import enum


class ResourceEnum(enum.Enum):
    def __str__(self):
        return str(self.value)


class ReleaseStatus(ResourceEnum):
    STATUS_UNSPECIFIED = 'statusUnspecified'
    DRAFT = 'draft'
    IN_PROGRESS = 'inProgress'
    HALTED = 'halted'
    COMPLETED = 'completed'
