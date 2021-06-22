import enum


class ResourceEnum(enum.Enum):
    def __str__(self):
        return str(self.value)


class TrackName(ResourceEnum):
    INTERNAL = 'internal'
    ALPHA = 'alpha'
    BETA = 'beta'
    PRODUCTION = 'production'


class ReleaseStatus(ResourceEnum):
    STATUS_UNSPECIFIED = 'statusUnspecified'
    DRAFT = 'draft'
    IN_PROGRESS = 'inProgress'
    HALTED = 'halted'
    COMPLETED = 'completed'
