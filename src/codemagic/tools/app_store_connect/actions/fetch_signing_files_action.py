from __future__ import annotations

from abc import ABCMeta
from itertools import chain
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Colors
from codemagic.models import PrivateKey

from ..abstract_base_action import AbstractBaseAction
from ..arguments import BundleIdArgument
from ..arguments import CertificateArgument
from ..arguments import CommonArgument
from ..arguments import ProfileArgument
from ..arguments import Types
from ..errors import AppStoreConnectError


class FetchSigningFilesAction(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "fetch-signing-files",
        BundleIdArgument.BUNDLE_ID_IDENTIFIER,
        BundleIdArgument.PLATFORM,
        CertificateArgument.PRIVATE_KEY,
        CertificateArgument.PRIVATE_KEY_PASSWORD,
        CertificateArgument.P12_CONTAINER_PASSWORD,
        ProfileArgument.PROFILE_TYPE,
        BundleIdArgument.IDENTIFIER_STRICT_MATCH,
        CommonArgument.CREATE_RESOURCE,
    )
    def fetch_signing_files(
        self,
        bundle_id_identifier: str,
        certificate_key: Optional[Union[PrivateKey, Types.CertificateKeyArgument]] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
        p12_container_password: str = "",
        platform: BundleIdPlatform = BundleIdPlatform.IOS,
        profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
        bundle_id_identifier_strict_match: bool = False,
        create_resource: bool = False,
    ) -> Tuple[List[Profile], List[SigningCertificate]]:
        """
        Fetch provisioning profiles and code signing certificates
        for Bundle ID with given identifier
        """

        private_key = self._get_certificate_key(certificate_key, certificate_key_password)
        if private_key is None:
            raise AppStoreConnectError(f"Cannot save {SigningCertificate.s} without certificate private key")

        bundle_ids = self._get_or_create_bundle_ids(
            bundle_id_identifier,
            platform,
            create_resource,
            bundle_id_identifier_strict_match,
        )
        self.echo("")

        certificates = self._get_or_create_certificates(
            profile_type,
            certificate_key,
            certificate_key_password,
            create_resource,
        )
        self.echo("")

        profiles = self._get_or_create_profiles(
            bundle_ids,
            certificates,
            profile_type,
            create_resource,
            platform,
        )
        self.echo("")

        self._save_certificates(certificates, private_key, p12_container_password)
        self._save_profiles(profiles)
        return profiles, certificates

    def _get_or_create_bundle_ids(
        self,
        bundle_id_identifier: str,
        platform: BundleIdPlatform,
        create_resource: bool,
        strict_match: bool,
    ) -> List[BundleId]:
        bundle_ids = self.list_bundle_ids(
            bundle_id_identifier,
            platform=platform,
            bundle_id_identifier_strict_match=strict_match,
            should_print=False,
        )
        if not bundle_ids:
            if not create_resource:
                raise AppStoreConnectError(f"Did not find {BundleId.s} with identifier {bundle_id_identifier}")
            bundle_ids.append(self.create_bundle_id(bundle_id_identifier, platform=platform, should_print=False))
        else:
            for bundle_id in bundle_ids:
                self.logger.info(f"- {bundle_id.attributes.name} {bundle_id.attributes.identifier} ({bundle_id.id})")
        return bundle_ids

    def _get_or_create_certificates(
        self,
        profile_type: ProfileType,
        certificate_key: Optional[Union[PrivateKey, Types.CertificateKeyArgument]],
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument],
        create_resource: bool,
    ) -> List[SigningCertificate]:
        certificate_types = CertificateType.resolve_applicable_types(profile_type=profile_type)

        certificates = self.list_certificates(
            certificate_types=certificate_types,
            certificate_key=certificate_key,
            certificate_key_password=certificate_key_password,
            should_print=False,
        )

        if not certificates:
            if not create_resource:
                _certificate_types = ", ".join(map(str, certificate_types))
                raise AppStoreConnectError(f"Did not find {SigningCertificate.s} with type {_certificate_types}")
            certificate = self.create_certificate(
                certificate_types[0],
                certificate_key=certificate_key,
                certificate_key_password=certificate_key_password,
                should_print=False,
            )
            certificates.append(certificate)
        return certificates

    def _get_or_create_profiles(
        self,
        bundle_ids: Sequence[BundleId],
        certificates: Sequence[SigningCertificate],
        profile_type: ProfileType,
        create_resource: bool,
        platform: Optional[BundleIdPlatform] = None,
    ):
        def has_certificate(profile) -> bool:
            try:
                profile_certificates = self.api_client.profiles.list_certificate_ids(profile)
                return bool(certificate_ids.issubset({c.id for c in profile_certificates}))
            except AppStoreConnectApiError as err:
                error = f"Listing {SigningCertificate.s} for {Profile} {profile.id} failed unexpectedly"
                self.logger.warning(Colors.YELLOW(f"{error}: {err.error_response}"))
                return False

        def missing_profile(bundle_id) -> bool:
            try:
                bundle_ids_profiles = self.api_client.bundle_ids.list_profile_ids(bundle_id)
                return not (profile_ids & {p.id for p in bundle_ids_profiles})
            except AppStoreConnectApiError as err:
                error = f"Listing {Profile.s} for {BundleId} {bundle_id.id} failed unexpectedly"
                self.logger.warning(Colors.YELLOW(f"{error}: {err.error_response}"))
                return True

        certificate_ids = {c.id for c in certificates}
        profiles = self.list_bundle_id_profiles(
            [bundle_id.id for bundle_id in bundle_ids],
            profile_type=profile_type,
            profile_state=ProfileState.ACTIVE,
            should_print=False,
        )
        profiles = list(filter(has_certificate, profiles))

        certificate_names = ", ".join(c.get_display_info() for c in certificates)
        message = f"that contain {SigningCertificate.plural(len(certificates))} {certificate_names}"
        self.printer.log_filtered(Profile, profiles, message)
        for profile in profiles:
            self.logger.info(f"- {profile.get_display_info()}")

        profile_ids = {p.id for p in profiles}
        bundle_ids_without_profiles = list(filter(missing_profile, bundle_ids))
        if bundle_ids_without_profiles and not create_resource:
            missing = ", ".join(f'"{bid.attributes.identifier}" [{bid.id}]' for bid in bundle_ids_without_profiles)
            raise AppStoreConnectError(f"Did not find {profile_type} {Profile.s} for {BundleId.s}: {missing}")

        created_profiles = self._create_missing_profiles(
            bundle_ids_without_profiles,
            certificates,
            profile_type,
            platform,
        )
        profiles.extend(created_profiles)
        return profiles

    def _create_missing_profiles(
        self,
        bundle_ids_without_profiles: Sequence[BundleId],
        seed_certificates: Sequence[SigningCertificate],
        profile_type: ProfileType,
        platform: Optional[BundleIdPlatform] = None,
    ) -> Iterator[Profile]:
        if not bundle_ids_without_profiles:
            return
        if platform is None:
            platform = bundle_ids_without_profiles[0].attributes.platform

        devices = self.list_devices(platform=platform, device_status=DeviceStatus.ENABLED, should_print=False)
        certificates = self.list_certificates(profile_type=profile_type, should_print=False)
        certificate_ids = list({c.id for c in chain(seed_certificates, certificates)})
        device_ids = [d.id for d in devices if d.attributes.deviceClass.is_compatible(profile_type)]

        for bundle_id in bundle_ids_without_profiles:
            yield self.create_profile(
                bundle_id.id,
                certificate_ids,
                device_ids,
                profile_type=profile_type,
                should_print=False,
            )
