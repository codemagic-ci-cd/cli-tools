from __future__ import annotations

import pathlib
import re
import tempfile
from typing import List
from typing import Optional
from typing import Sequence

from codemagic.apple.resources import Profile
from codemagic.apple.resources import SigningCertificate
from codemagic.models import Certificate
from codemagic.models import PrivateKey

from ..errors import AppStoreConnectError
from ..resource_printer import ResourcePrinter


class SigningFileSaverMixin:
    certificates_directory: pathlib.Path
    printer: ResourcePrinter
    profiles_directory: pathlib.Path

    @classmethod
    def _get_unique_path(cls, file_name: str, destination: pathlib.Path) -> pathlib.Path:
        if destination.exists() and not destination.is_dir():
            raise ValueError(f"Destination {destination} is not a directory")
        destination.mkdir(parents=True, exist_ok=True)
        name = pathlib.Path(re.sub(r"[^\w.]", "_", file_name))
        tf = tempfile.NamedTemporaryFile(
            prefix=f"{name.stem}_",
            suffix=name.suffix,
            dir=destination,
            delete=False,
        )
        tf.close()
        return pathlib.Path(tf.name)

    def _save_profile(self, profile: Profile) -> pathlib.Path:
        profile_path = self._get_unique_path(
            f"{profile.attributes.profileType}_{profile.id}{profile.profile_extension}",
            self.profiles_directory,
        )
        profile_path.write_bytes(profile.profile_content)
        self.printer.log_saved(profile, profile_path)
        return profile_path

    def _save_certificate(
        self,
        certificate: SigningCertificate,
        private_key: PrivateKey,
        p12_container_password: str,
        certificate_save_path: Optional[pathlib.Path] = None,
    ) -> pathlib.Path:
        if certificate_save_path is None:
            certificate_path = self._get_unique_path(
                f"{certificate.attributes.certificateType}_{certificate.id}.p12",
                self.certificates_directory,
            )
        else:
            certificate_path = certificate_save_path
        try:
            p12_path = Certificate.from_ans1(certificate.asn1_content).export_p12(
                private_key,
                p12_container_password,
                export_path=certificate_path,
            )
        except (ValueError, IOError) as error:
            raise AppStoreConnectError(*error.args)
        self.printer.log_saved(certificate, p12_path)
        return p12_path

    def _save_profiles(self, profiles: Sequence[Profile]) -> List[pathlib.Path]:
        return [self._save_profile(profile) for profile in profiles]

    def _save_certificates(
        self,
        certificates: Sequence[SigningCertificate],
        private_key: PrivateKey,
        p12_container_password: str,
    ) -> List[pathlib.Path]:
        return [self._save_certificate(c, private_key, p12_container_password) for c in certificates]
