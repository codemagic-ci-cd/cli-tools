import contextlib
import enum
import re

from codemagic.utilities import log


class ResourceEnumMeta(enum.EnumMeta):
    """
    Custom metaclass for Resource enumerations to accommodate the cases when
    App Store Connect API returns such a value that our definitions do not describe.
    For example, `BundleIdPlatform` should only have values `IOS` and `MAC_OS` as per
    documentation https://developer.apple.com/documentation/appstoreconnectapi/bundleidplatform,
    but it is known that in practice `UNIVERSAL` and `SERVICES` are just as valid values.
    Without this graceful fallback to dynamically generated enumeration the program execution
    fails unexpectedly, which is not desirable.
    """

    graceful_fallback = True
    enable_name_transformation = False

    def __call__(cls, value, *args, **kwargs):  # noqa: N805
        try:
            return super().__call__(value, *args, **kwargs)
        except ValueError as ve:
            if not cls.graceful_fallback:
                cls._transform_class_name()
                raise
            logger = log.get_logger(cls, log_to_stream=False)
            logger.warning('Undefined Resource enumeration: %s', ve)
            try:
                enum_class = ResourceEnum(f'Graceful{cls.__name__}', {value: value})
                return enum_class(value)
            except TypeError:
                raise ve

    def _transform_class_name(cls):  # noqa: N805
        """
        If enabled, transform CamelCase class name 'ClassName' to more
        readable 'class name', which appears prettier in argparse error messages.
        """
        if not cls.enable_name_transformation:
            return
        formatted_name = re.sub(r'([A-Z])', lambda m: f' {m.group(1).lower()}', cls.__name__)
        cls.__name__ = formatted_name.strip()

    @staticmethod
    @contextlib.contextmanager
    def cli_arguments_parsing_mode():
        original_graceful_fallback = ResourceEnumMeta.graceful_fallback
        original_enable_name_transformation = ResourceEnumMeta.enable_name_transformation

        # Turn off graceful enumeration fallback to get proper error messages
        ResourceEnumMeta.graceful_fallback = False
        # Enable name transformation to obtain pretty argparse error messages
        ResourceEnumMeta.enable_name_transformation = True
        try:
            yield
        finally:
            ResourceEnumMeta.graceful_fallback = original_graceful_fallback
            ResourceEnumMeta.enable_name_transformation = original_enable_name_transformation

    @staticmethod
    @contextlib.contextmanager
    def without_graceful_fallback():
        original_value = ResourceEnumMeta.graceful_fallback
        ResourceEnumMeta.graceful_fallback = False
        try:
            yield
        finally:
            ResourceEnumMeta.graceful_fallback = original_value


class ResourceEnum(enum.Enum, metaclass=ResourceEnumMeta):

    def __str__(self):
        return str(self.value)
