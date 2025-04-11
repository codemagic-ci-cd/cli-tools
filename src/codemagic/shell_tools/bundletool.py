import pathlib
from functools import lru_cache
from typing import Literal
from typing import Optional

import codemagic

from .java_jar_tool import JavaJarTool

DEFAULT_BUNDLETOOL_PATH: Optional[pathlib.Path] = None


@lru_cache(1)
def find_included_bundletool_jar() -> pathlib.Path:
    data_dir = pathlib.Path(codemagic.__file__).parent / "data"
    bundletool_jar = next(data_dir.rglob("bundletool*.jar"), None)
    if not bundletool_jar:
        raise IOError(f"Bundletool jar not available in {data_dir}")
    return bundletool_jar.resolve()


class Bundletool(JavaJarTool):
    """
    Python bindings for Bundletool
    https://developer.android.com/tools/bundletool
    """

    def _get_jar_path(self, jar_path: Optional[pathlib.Path] = None) -> pathlib.Path:
        if jar_path:
            return jar_path
        try:
            return find_included_bundletool_jar()
        except IOError:
            if DEFAULT_BUNDLETOOL_PATH:
                return DEFAULT_BUNDLETOOL_PATH
            raise

    def version(self, show_output: bool = True) -> str:
        """
        Get bundletool version.

        See full usage instructions with `java -jar bundletool.jar help version`.
        """
        completed_process = self._run_command(
            (self.java, "-jar", self.jar, "version"),
            show_output=show_output,
        )
        return self._get_stdout(completed_process).strip()

    def dump(
        self,
        target: Literal["manifest", "resources", "config", "runtime-enabled-sdk-config"],
        bundle: pathlib.Path,
        *,
        module: Optional[str] = None,
        resource: Optional[str] = None,
        values: Optional[bool] = None,
        xpath: Optional[str] = None,
        show_output: bool = True,
    ) -> str:
        """
        Get files or extract values from the bundle in a human-readable form.

        See full usage instructions with `java -jar bundletool.jar help dump`.
        """
        if target != "manifest" and xpath:
            raise ValueError("XPath expression can only be used when dumping manifest")
        elif target != "manifest" and module:
            raise ValueError("Module can only be used when dumping manifest")
        elif target != "resources" and values:
            raise ValueError("Printing resource values can only be requested when dumping resources")
        elif target != "resources" and resource:
            raise ValueError("The resource name or id can only be used when dumping resources")

        cmd = [
            *(self.java, "-jar", self.jar),
            "dump",
            target,
            *("--bundle", bundle),
        ]
        if module:
            cmd.extend(("--module", module))
        if resource:
            cmd.extend(("--resource", resource))
        if values:
            cmd.append("--values")
        if xpath:
            cmd.extend(("--xpath", xpath))

        completed_process = self._run_command(cmd, show_output=show_output)
        return self._get_stdout(completed_process)

    def validate(
        self,
        bundle: pathlib.Path,
        *,
        show_output: bool = True,
    ) -> str:
        """
        Verifies the given Android App Bundle is valid and outputs information about it.

        See full usage instructions with `java -jar bundletool.jar help verify`.
        """
        completed_process = self._run_command(
            (self.java, "-jar", self.jar, "validate", "--bundle", bundle),
            show_output=show_output,
        )
        return self._get_stdout(completed_process)

    def build_apks(
        self,
        bundle: pathlib.Path,
        output: pathlib.Path,
        *,
        mode: Optional[Literal["default", "universal", "system", "persistent", "instant", "archive"]],
        keystore: Optional[pathlib.Path] = None,
        keystore_password: Optional[str] = None,
        key_alias: Optional[str] = None,
        key_password: Optional[str] = None,
        show_output: bool = True,
    ):
        """
        Generate an APK Set archive containing either all possible split APKs and standalone APKs.

        See full usage instructions with `java -jar bundletool.jar help build-apks`.
        """
        cmd = [
            *(self.java, "-jar", self.jar),
            "build-apks",
            *("--bundle", bundle),
            *("--output", output),
        ]
        if mode:
            cmd.extend(("--mode", mode))

        obfuscate_patterns = []
        if keystore:
            cmd.extend(("--ks", keystore))
        if keystore_password:
            obfuscate_patterns.append(f"pass:{keystore_password}")
            cmd.extend(("--ks-pass", f"pass:{keystore_password}"))
        if key_alias:
            cmd.extend(("--ks-key-alias", key_alias))
        if key_password:
            obfuscate_patterns.append(f"pass:{key_password}")
            cmd.extend(("--key-pass", f"pass:{key_password}"))

        self._run_command(
            cmd,
            obfuscate_patterns=obfuscate_patterns,
            show_output=show_output,
        )
