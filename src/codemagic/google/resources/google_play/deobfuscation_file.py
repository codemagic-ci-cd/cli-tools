import dataclasses

from codemagic.google.resources import Resource

from .deobfuscation_file_type import DeobfuscationFileType


@dataclasses.dataclass
class DeobfuscationFile(Resource):
    symbolType: DeobfuscationFileType

    def __post_init__(self):
        if isinstance(self.symbolType, str):
            self.symbolType = DeobfuscationFileType(self.symbolType)
