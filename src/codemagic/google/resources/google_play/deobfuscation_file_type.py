from codemagic.models.enums import ResourceEnum


class DeobfuscationFileType(ResourceEnum):
    """
    https://developers.google.com/android-publisher/api-ref/rest/v3/edits.deobfuscationfiles#DeobfuscationFileType
    """

    UNSPECIFIED = "deobfuscationFileTypeUnspecified"
    PROGUARD = "proguard"
    NATIVE_CODE = "nativeCode"
