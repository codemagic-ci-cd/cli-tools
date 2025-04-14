from __future__ import annotations

import json
import pathlib
import subprocess
import zipfile
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from typing import overload

from codemagic import cli
from codemagic.mixins import PathFinderMixin
from codemagic.models import AndroidSigningInfo
from codemagic.shell_tools import Bundletool
from codemagic.shell_tools.jarsigner import Jarsigner


class AndroidAppBundleTypes:
    class KeyAlias(str):
        pass

    class _Password(cli.EnvironmentArgumentValue[str]):
        @classmethod
        def _is_valid(cls, value: str) -> bool:
            return bool(value)

    class KeystorePassword(_Password):
        environment_variable_key = "KEYSTORE_PASSWORD"

    class KeyPassword(_Password):
        environment_variable_key = "KEYSTORE_KEY_PASSWORD"


class AndroidAppBundleError(cli.CliAppException):
    pass


class BundleToolJarPathArgument(cli.TypedCliArgument[pathlib.Path]):
    argument_type = cli.CommonArgumentTypes.existing_path
    environment_variable_key = "ANDROID_APP_BUNDLE_BUNDLETOOL"


class AndroidAppBundleArgument(cli.Argument):
    BUNDLETOOL_JAR = cli.ArgumentProperties(
        flags=("--bundletool",),
        key="bundletool_jar",
        type=BundleToolJarPathArgument,
        description="Specify path to bundletool jar that will be used in place of the included version.",
        argparse_kwargs={"required": False},
    )
    BUNDLE_PATTERN = cli.ArgumentProperties(
        flags=("--bundle",),
        key="aab_pattern",
        type=pathlib.Path,
        description="Glob pattern to parse files, relative to current folder",
        argparse_kwargs={
            "default": "**/*.aab",
            "required": False,
        },
    )
    BUNDLE_PATH = cli.ArgumentProperties(
        flags=("--bundle",),
        key="aab_path",
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to Android app bundle file",
        argparse_kwargs={
            "required": True,
        },
    )
    KEYSTORE_PATH = cli.ArgumentProperties(
        flags=("--ks",),
        key="keystore_path",
        type=cli.CommonArgumentTypes.existing_path,
        description="Path to the keystore to sign the apk files with",
        argparse_kwargs={
            "default": None,
            "required": False,
        },
    )
    KEYSTORE_PATH_REQUIRED = cli.ArgumentProperties.duplicate(
        KEYSTORE_PATH,
        argparse_kwargs={"required": True},
    )
    KEYSTORE_PASSWORD = cli.ArgumentProperties(
        flags=("--ks-pass",),
        key="keystore_password",
        type=AndroidAppBundleTypes.KeystorePassword,
        description="Keystore password",
        argparse_kwargs={
            "default": None,
            "required": False,
        },
    )
    KEYSTORE_PASSWORD_REQUIRED = cli.ArgumentProperties.duplicate(
        KEYSTORE_PASSWORD,
        argparse_kwargs={"required": True},
    )
    KEY_ALIAS = cli.ArgumentProperties(
        flags=("--ks-key-alias",),
        key="key_alias",
        type=AndroidAppBundleTypes.KeyAlias,
        description="Keystore key alias",
        argparse_kwargs={
            "default": None,
            "required": False,
        },
    )
    KEY_ALIAS_REQUIRED = cli.ArgumentProperties.duplicate(
        KEY_ALIAS,
        argparse_kwargs={"required": True},
    )
    KEY_PASSWORD = cli.ArgumentProperties(
        flags=("--key-pass",),
        key="key_password",
        type=AndroidAppBundleTypes.KeyPassword,
        description="Keystore key password",
        argparse_kwargs={
            "default": None,
            "required": False,
        },
    )
    KEY_PASSWORD_REQUIRED = cli.ArgumentProperties.duplicate(
        KEY_PASSWORD,
        argparse_kwargs={"required": True},
    )
    BUILD_APKS_MODE = cli.ArgumentProperties(
        flags=("--mode",),
        key="mode",
        description=(
            "Set the mode to universal if you want bundletool to build only a single APK "
            "that includes all of your app's code and resources such that the APK is "
            "compatible with all device configurations your app supports."
        ),
        argparse_kwargs={
            "default": None,
            "required": False,
            "choices": ["universal"],
        },
    )
    DUMP_TARGET = cli.ArgumentProperties(
        key="target",
        description="Target of the dump",
        argparse_kwargs={
            "choices": [
                "manifest",
                "resources",
                "config",
                "runtime-enabled-sdk-config",
            ],
        },
    )
    DUMP_XPATH = cli.ArgumentProperties(
        flags=("--xpath",),
        key="xpath",
        description=(
            "XML path to specific attribute in the target. "
            'For example "/manifest/@android:versionCode" to obtain the version code from manifest. '
            "If not given, the full target will be dumped."
        ),
        argparse_kwargs={
            "required": False,
        },
    )
    DUMP_MODULE = cli.ArgumentProperties(
        flags=("--module",),
        key="module",
        description=(
            "Name of the module to apply the dump for. Only applies when dumping the manifest. Defaults to 'base'."
        ),
        argparse_kwargs={
            "required": False,
        },
    )
    DUMP_RESOURCE = cli.ArgumentProperties(
        key="resource",
        flags=("--resource",),
        description=(
            "Name or ID of the resource to lookup. Only applies when dumping resources. "
            "If a resource ID is provided, it can be specified either as a decimal or hexadecimal integer. "
            "If a resource name is provided, it must follow the format '<type>/<name>', e.g. 'drawable/icon'"
        ),
        argparse_kwargs={
            "required": False,
        },
    )
    DUMP_VALUES = cli.ArgumentProperties(
        key="values",
        flags=("--values",),
        type=bool,
        description=(
            "When set, also prints the values of the resources. Defaults to false. "
            "Only applies when dumping the resources."
        ),
        argparse_kwargs={
            "required": False,
            "action": "store_true",
        },
    )
    JSON_OUTPUT = cli.ArgumentProperties(
        key="json_output",
        flags=("--json", "-j"),
        type=bool,
        description="Whether to show the information in JSON format",
        argparse_kwargs={"required": False, "action": "store_true"},
    )


KeystorePassword = Union[str, AndroidAppBundleTypes.KeystorePassword]
KeyAlias = Union[str, AndroidAppBundleTypes.KeyAlias]
KeyPassword = Union[str, AndroidAppBundleTypes.KeyPassword]


class AndroidAppBundleActionGroup(cli.ActionGroup):
    BUNDLETOOL = cli.ActionGroupProperties(
        name="bundletool",
        description="Show information about Bundletool",
    )


@cli.common_arguments(
    AndroidAppBundleArgument.BUNDLETOOL_JAR,
)
class AndroidAppBundle(cli.CliApp, PathFinderMixin):
    """
    Manage Android App Bundles using
    [Bundletool](https://developer.android.com/studio/command-line/bundletool)
    """

    def __init__(self, bundletool_jar: Optional[pathlib.Path | BundleToolJarPathArgument] = None, **kwargs):
        super().__init__(**kwargs)
        self._bundletool_jar = BundleToolJarPathArgument.resolve_value(bundletool_jar) if bundletool_jar else None

    def _get_bundletool(self) -> Bundletool:
        return Bundletool(jar=self._bundletool_jar)

    @classmethod
    @overload
    def _get_password_value(cls, password: Union[KeyPassword, KeystorePassword]) -> str: ...

    @classmethod
    @overload
    def _get_password_value(cls, password: None) -> None: ...

    @classmethod
    def _get_password_value(cls, password: Optional[Union[KeyPassword, KeystorePassword]]) -> Optional[str]:
        if password is None:
            return None
        elif isinstance(password, str):
            return password
        elif isinstance(password, (AndroidAppBundleTypes.KeystorePassword, AndroidAppBundleTypes.KeyPassword)):
            return password.value
        raise TypeError(f"Invalid type {type(password)} for password")

    @classmethod
    @overload
    def _convert_cli_args_to_signing_info(
        cls,
        keystore_path: pathlib.Path,
        keystore_password: KeystorePassword,
        key_alias: KeyAlias,
        key_password: KeyPassword,
    ) -> AndroidSigningInfo: ...

    @classmethod
    @overload
    def _convert_cli_args_to_signing_info(
        cls,
        keystore_path: Optional[pathlib.Path],
        keystore_password: Optional[KeystorePassword],
        key_alias: Optional[KeyAlias],
        key_password: Optional[KeyPassword],
    ) -> Optional[AndroidSigningInfo]: ...

    @classmethod
    def _convert_cli_args_to_signing_info(
        cls,
        keystore_path: Optional[pathlib.Path],
        keystore_password: Optional[KeystorePassword],
        key_alias: Optional[KeyAlias],
        key_password: Optional[KeyPassword],
    ) -> Optional[AndroidSigningInfo]:
        keystore_password_value = cls._get_password_value(keystore_password)
        key_password_value = cls._get_password_value(key_password)
        if keystore_path and keystore_password_value and key_alias and key_password_value:
            return AndroidSigningInfo(
                store_path=keystore_path,
                store_pass=keystore_password_value,
                key_alias=str(key_alias),
                key_pass=key_password_value,
            )
        elif keystore_path or keystore_password_value or key_alias or key_password_value:
            error_msg = "Either all signing info arguments should be specified, or none of them should"
            raise AndroidAppBundleArgument.KEYSTORE_PATH.raise_argument_error(error_msg)
        else:
            return None

    def _get_aab_paths_from_pattern(self, pattern: pathlib.Path) -> List[pathlib.Path]:
        def is_valid_aab(aab_path):  # Exclude intermediate Android app bundles
            return "intermediates" not in aab_path.parts

        if pattern.is_file():  # No need to glob in case of verbatim path
            aab_paths = [pattern]
        else:
            aab_paths = [aab for aab in self.find_paths(pattern) if is_valid_aab(aab)]
            if not aab_paths:
                error_msg = "Did not find any matching Android app bundles from which to generate APKs"
                raise AndroidAppBundleError(error_msg)
            self.logger.info(f"Found {len(aab_paths)} matching files")

        return aab_paths

    @cli.action(
        "build-apks",
        AndroidAppBundleArgument.BUNDLE_PATTERN,
        AndroidAppBundleArgument.KEYSTORE_PATH,
        AndroidAppBundleArgument.KEYSTORE_PASSWORD,
        AndroidAppBundleArgument.KEY_ALIAS,
        AndroidAppBundleArgument.KEY_PASSWORD,
        AndroidAppBundleArgument.BUILD_APKS_MODE,
    )
    def build_apks(
        self,
        aab_pattern: pathlib.Path,
        keystore_path: Optional[pathlib.Path] = None,
        keystore_password: Optional[KeystorePassword] = None,
        key_alias: Optional[KeyAlias] = None,
        key_password: Optional[KeyPassword] = None,
        mode: Optional[Literal["default", "universal", "system", "persistent", "instant", "archive"]] = None,
        should_print: bool = True,
    ) -> List[pathlib.Path]:
        """
        Generates an APK Set archive containing either all possible split APKs and
        standalone APKs or APKs optimized for the connected device (see connected-
        device flag). Returns list of generated APK set archives
        """
        signing_info = self._convert_cli_args_to_signing_info(
            keystore_path,
            keystore_password,
            key_alias,
            key_password,
        )

        apks_paths = []
        for aab_path in self._get_aab_paths_from_pattern(aab_pattern):
            apks_path = self._build_apk_set_archive(
                aab_path,
                signing_info=signing_info,
                mode=mode,
            )
            apks_paths.append(apks_path)
            if should_print:
                self.echo(str(apks_path))
        return apks_paths

    @cli.action(
        "build-universal-apk",
        AndroidAppBundleArgument.BUNDLE_PATTERN,
        AndroidAppBundleArgument.KEYSTORE_PATH,
        AndroidAppBundleArgument.KEYSTORE_PASSWORD,
        AndroidAppBundleArgument.KEY_ALIAS,
        AndroidAppBundleArgument.KEY_PASSWORD,
    )
    def build_universal_apks(
        self,
        aab_pattern: pathlib.Path,
        keystore_path: Optional[pathlib.Path] = None,
        keystore_password: Optional[KeystorePassword] = None,
        key_alias: Optional[KeyAlias] = None,
        key_password: Optional[KeyPassword] = None,
    ) -> List[pathlib.Path]:
        """
        Shortcut for `build-apks` to build universal APKs from bundles
        """

        apks_paths = self.build_apks(
            aab_pattern,
            keystore_path=keystore_path,
            keystore_password=keystore_password,
            key_alias=key_alias,
            key_password=key_password,
            mode="universal",
            should_print=False,
        )

        apk_paths = []
        for apks_path in apks_paths:
            apk_path = self._extract_universal_apk(apks_path)
            apk_paths.append(apk_path)
            self.echo(str(apk_path))
            apks_path.unlink()

        return apk_paths

    @cli.action(
        "dump",
        AndroidAppBundleArgument.DUMP_TARGET,
        AndroidAppBundleArgument.BUNDLE_PATH,
        AndroidAppBundleArgument.DUMP_MODULE,
        AndroidAppBundleArgument.DUMP_RESOURCE,
        AndroidAppBundleArgument.DUMP_VALUES,
        AndroidAppBundleArgument.DUMP_XPATH,
    )
    def dump(
        self,
        target: Literal["manifest", "resources", "config", "runtime-enabled-sdk-config"],
        aab_path: pathlib.Path,
        xpath: Optional[str] = None,
        module: Optional[str] = None,
        resource: Optional[str] = None,
        values: Optional[bool] = None,
    ) -> str:
        """
        Get files list or extract values from the bundle in a human-readable form
        """
        if target != "manifest" and xpath:
            error = "XPath expression can only be used when dumping manifest"
            raise AndroidAppBundleArgument.DUMP_XPATH.raise_argument_error(error)
        elif target != "manifest" and module:
            error = "Module can only be used when dumping manifest"
            raise AndroidAppBundleArgument.DUMP_MODULE.raise_argument_error(error)
        elif target != "resources" and values:
            error = "Printing resource values can only be requested when dumping resources"
            raise AndroidAppBundleArgument.DUMP_VALUES.raise_argument_error(error)
        elif target != "resources" and resource:
            error = "The resource name or id can only be used when dumping resources"
            raise AndroidAppBundleArgument.DUMP_RESOURCE.raise_argument_error(error)

        if xpath:
            self.logger.info(f'Dump attribute "{xpath}" from target "{target}" from {aab_path}')
        else:
            self.logger.info(f'Dump target "{target}" from {aab_path}')

        try:
            return self._get_bundletool().dump(
                target,
                aab_path,
                module=module,
                resource=resource,
                values=values,
                xpath=xpath,
            )
        except subprocess.CalledProcessError as cpe:
            message = f"Unable to dump {target} for bundle {aab_path}"
            raise AndroidAppBundleError(message, called_process_error=cpe) from cpe

    @cli.action(
        "sign",
        AndroidAppBundleArgument.BUNDLE_PATH,
        AndroidAppBundleArgument.KEYSTORE_PATH_REQUIRED,
        AndroidAppBundleArgument.KEYSTORE_PASSWORD_REQUIRED,
        AndroidAppBundleArgument.KEY_ALIAS_REQUIRED,
        AndroidAppBundleArgument.KEY_PASSWORD_REQUIRED,
    )
    def sign(
        self,
        aab_path: pathlib.Path,
        keystore_path: pathlib.Path,
        keystore_password: KeystorePassword,
        key_alias: KeyAlias,
        key_password: KeyPassword,
    ):
        """
        Sign Android app bundle with specified key and keystore
        """
        signing_info = self._convert_cli_args_to_signing_info(
            keystore_path,
            keystore_password,
            key_alias,
            key_password,
        )

        self.logger.info(f"Sign {aab_path}")
        try:
            Jarsigner().sign(
                aab_path,
                keystore=signing_info.store_path,
                keystore_password=signing_info.store_pass,
                key_alias=signing_info.key_alias,
                key_password=signing_info.key_pass,
                verbose=True,
                show_output=False,
            )
        except subprocess.CalledProcessError as cpe:
            message = f"Unable to sign bundle {aab_path}"
            raise AndroidAppBundleError(message, called_process_error=cpe) from cpe

    @cli.action("is-signed", AndroidAppBundleArgument.BUNDLE_PATH)
    def is_signed(self, aab_path: pathlib.Path):
        """
        Check if given Android app bundle is signed
        """
        try:
            verify_output = Jarsigner().verify(
                aab_path,
                verbose=True,
                show_output=False,
            )
        except subprocess.CalledProcessError as cpe:
            message = f"Unable to check if {aab_path} is signed"
            raise AndroidAppBundleError(message, called_process_error=cpe) from cpe

        if "jar is unsigned" in verify_output:
            raise AndroidAppBundleError(f"Bundle {aab_path} is not signed")

        self.echo(f"Bundle {aab_path} is signed")

    @cli.action("validate", AndroidAppBundleArgument.BUNDLE_PATH)
    def validate(self, aab_path: pathlib.Path) -> str:
        """
        Verify that given Android App Bundle is valid and print out information about it
        """
        self.logger.info(f"Validate {aab_path}")
        try:
            return self._get_bundletool().validate(aab_path)
        except subprocess.CalledProcessError as cpe:
            raise AndroidAppBundleError(f"Unable to validate {aab_path}", called_process_error=cpe) from cpe

    @cli.action(
        "version",
        action_group=AndroidAppBundleActionGroup.BUNDLETOOL,
        deprecation_info=cli.ActionDeprecationInfo("bundletool-version", "0.58.0"),
    )
    def bundletool_version(self) -> str:
        """
        Get Bundletool version
        """
        self.logger.info("Get Bundletool version")
        try:
            return self._get_bundletool().version()
        except subprocess.CalledProcessError as cpe:
            raise AndroidAppBundleError("Unable to get Bundletool version", called_process_error=cpe) from cpe

    @cli.action(
        "info",
        AndroidAppBundleArgument.JSON_OUTPUT,
        action_group=AndroidAppBundleActionGroup.BUNDLETOOL,
    )
    def bundletool_info(self, json_output: bool = False):
        """
        Show full information about Bundletool runtime environment
        """
        try:
            bundletool = self._get_bundletool()
            version = bundletool.version(show_output=False)
        except IOError as ioe:
            raise AndroidAppBundleError(str(ioe)) from ioe
        except subprocess.CalledProcessError as cpe:
            raise AndroidAppBundleError("Unable to get Bundletool version", called_process_error=cpe) from cpe

        if json_output:
            self.echo(json.dumps({"java": str(bundletool.java), "bundletool": str(bundletool.jar), "version": version}))
        else:
            self.echo(f"Bundletool version: {version}")
            self.echo(f"Bundletool: {bundletool.jar}")
            self.echo(f"Java: {bundletool.java}")

    def _build_apk_set_archive(
        self,
        aab_path: pathlib.Path,
        *,
        signing_info: Optional[AndroidSigningInfo] = None,
        mode: Optional[Literal["default", "universal", "system", "persistent", "instant", "archive"]] = None,
    ) -> pathlib.Path:
        self.logger.info(f"Generating APKs from bundle {aab_path}")
        apks_path = aab_path.parent / f"{aab_path.stem}.apks"

        try:
            self._get_bundletool().build_apks(
                aab_path,
                apks_path,
                mode=mode,
                keystore=signing_info.store_path if signing_info else None,
                keystore_password=signing_info.store_pass if signing_info else None,
                key_alias=signing_info.key_alias if signing_info else None,
                key_password=signing_info.key_pass if signing_info else None,
            )
        except subprocess.CalledProcessError as cpe:
            message = f"Unable to generate apks file for bundle {aab_path}"
            raise AndroidAppBundleError(message, called_process_error=cpe) from cpe

        self.logger.info(f"Generated {apks_path}")
        return apks_path

    def _extract_universal_apk(self, apks_path: pathlib.Path) -> pathlib.Path:
        self.logger.info(f"Extracting universal APK from {apks_path}")
        apk_path = apks_path.parent / f"{apks_path.stem}-universal.apk"
        with zipfile.ZipFile(apks_path, "r") as zf, apk_path.open("wb+") as of:
            of.write(zf.read("universal.apk"))
        self.logger.info(f"Extracted {apk_path}")
        return apk_path


if __name__ == "__main__":
    AndroidAppBundle.invoke_cli()
