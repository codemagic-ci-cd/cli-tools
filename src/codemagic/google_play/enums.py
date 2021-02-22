import enum


class _ResourceEnum(enum.Enum):
    def __str__(self):
        return str(self.value)

class Track(_ResourceEnum):
    INTERNAL = 'internal'
    ALPHA = 'alpha'
    BETA = 'beta'
    PRODUCTION = 'production'