import enum


class _ResourceEnum(enum.Enum):
    def __str__(self):
        return str(self.value)


class TrackName(_ResourceEnum):
    INTERNAL = 'internal'
    ALPHA = 'alpha'
    BETA = 'beta'
    PRODUCTION = 'production'


class ReleaseStatus(_ResourceEnum):
    STATUS_UNSPECIFIED = 'statusUnspecified'
    DRAFT = 'draft'
    IN_PROGRESS = 'inProgress'
    HALTED = 'halted'
    COMPLETED = 'completed'
