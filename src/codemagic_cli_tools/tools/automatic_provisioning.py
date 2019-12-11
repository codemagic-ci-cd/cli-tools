#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization

from codemagic_cli_tools import cli
from codemagic_cli_tools import models
from codemagic_cli_tools.apple import AppStoreConnectApiError
from codemagic_cli_tools.apple.app_store_connect import AppStoreConnectApiClient
from codemagic_cli_tools.apple.app_store_connect import IssuerId
from codemagic_cli_tools.apple.app_store_connect import KeyIdentifier
from codemagic_cli_tools.apple.resources import BundleId
from codemagic_cli_tools.apple.resources import BundleIdPlatform
from codemagic_cli_tools.apple.resources import Certificate
from codemagic_cli_tools.apple.resources import CertificateType
from codemagic_cli_tools.apple.resources import Device
from codemagic_cli_tools.apple.resources import DeviceStatus
from codemagic_cli_tools.apple.resources import Profile
from codemagic_cli_tools.apple.resources import ProfileState
from codemagic_cli_tools.apple.resources import ProfileType
from codemagic_cli_tools.apple.resources import ResourceId
from codemagic_cli_tools.cli import Colors
from codemagic_cli_tools.cli.cli_types import ObfuscationPattern
from .provisioning.automatic_provisioning_arguments import AutomaticProvisioningArgument
from .provisioning.automatic_provisioning_arguments import BundleIdArgument
from .provisioning.automatic_provisioning_arguments import CertificateArgument
from .provisioning.automatic_provisioning_arguments import CommonArgument
from .provisioning.automatic_provisioning_arguments import DeviceArgument
from .provisioning.automatic_provisioning_arguments import ProfileArgument
from .provisioning.automatic_provisioning_arguments import Types
from .provisioning.base_provisioning import BaseProvisioning
from .provisioning.printer import Printer


class AutomaticProvisioningError(cli.CliAppException):
    pass


@cli.common_arguments(
    AutomaticProvisioningArgument.LOG_REQUESTS,
    AutomaticProvisioningArgument.ISSUER_ID,
    AutomaticProvisioningArgument.KEY_IDENTIFIER,
    AutomaticProvisioningArgument.PRIVATE_KEY,
    AutomaticProvisioningArgument.PRIVATE_KEY_PATH,
    AutomaticProvisioningArgument.JSON_OUTPUT,
)
class AutomaticProvisioning(BaseProvisioning):
    """
    Utility to download code signing certificates and provisioning profiles
    from Apple Developer Portal using App Store Connect API to perform iOS code signing.
    """

    def __init__(self,
                 key_identifier: KeyIdentifier,
                 issuer_id: IssuerId,
                 private_key: str,
                 log_requests: bool = False,
                 json_output: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.printer = Printer(self.logger, bool(json_output))
        self.api_client = AppStoreConnectApiClient(key_identifier, issuer_id, private_key, log_requests=log_requests)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace):
        key_identifier_argument = AutomaticProvisioningArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AutomaticProvisioningArgument.ISSUER_ID.from_args(cli_args)
        if issuer_id_argument is None:
            raise AutomaticProvisioningArgument.ISSUER_ID.raise_argument_error()
        if key_identifier_argument is None:
            raise AutomaticProvisioningArgument.KEY_IDENTIFIER.raise_argument_error()

        private_key_argument = AutomaticProvisioningArgument.PRIVATE_KEY.from_args(cli_args)
        private_key_path_argument = AutomaticProvisioningArgument.PRIVATE_KEY_PATH.from_args(cli_args)
        if private_key_argument is None and private_key_path_argument is None:
            raise AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error()
        if private_key_argument is not None and private_key_path_argument is not None:
            arguments = (AutomaticProvisioningArgument.PRIVATE_KEY, AutomaticProvisioningArgument.PRIVATE_KEY_PATH)
            given_arguments = ' and '.join(map(lambda k: Colors.CYAN(k.key.upper()), arguments))
            raise AutomaticProvisioningArgument.PRIVATE_KEY.raise_argument_error(
                f'Both {given_arguments} were given. Choose one.')

        if private_key_argument:
            private_key = private_key_argument.value
        else:
            private_key = private_key_path_argument.value.expanduser().read_text()

        return AutomaticProvisioning(
            issuer_id=issuer_id_argument.value,
            key_identifier=key_identifier_argument.value,
            private_key=private_key,
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            log_requests=cli_args.log_requests,
            json_output=cli_args.json_output,
        )

    def _list_resources(self, resource_filter, resource_manager, should_print):
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.printer.log_found(resource_manager.managed_resource, resources)
        self.printer.print_resources(resources, should_print)
        return resources

    def _delete_resource(self, resource_manager, resource_id: ResourceId, ignore_not_found: bool):
        resource_type = resource_manager.managed_resource
        self.printer.log_delete(resource_type, resource_id)
        try:
            resource_manager.delete(resource_id)
            self.printer.log_deleted(resource_type, resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found is True and api_error.status_code == 404:
                self.printer.log_ignore_not_deleted(resource_type, resource_id)
            else:
                raise AutomaticProvisioningError(str(api_error))

    @cli.action('list-devices',
                BundleIdArgument.PLATFORM,
                DeviceArgument.DEVICE_NAME,
                DeviceArgument.DEVICE_STATUS)
    def list_devices(self,
                     platform: Optional[BundleIdPlatform] = None,
                     device_name: Optional[str] = None,
                     device_status: Optional[DeviceStatus] = None,
                     should_print: bool = True) -> List[Device]:
        """
        List Devices from Apple Developer portal matching given constraints.
        """

        device_filter = self.api_client.devices.Filter(
            name=device_name, platform=platform, status=device_status)
        return self._list_resources(device_filter, self.api_client.devices, should_print)

    @cli.action('create-bundle-id',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM)
    def create_bundle_id(self,
                         bundle_id_identifier: str,
                         bundle_id_name: Optional[str] = None,
                         platform: BundleIdPlatform = BundleIdPlatform.IOS,
                         should_print: bool = True) -> BundleId:
        """
        Create Bundle ID in Apple Developer portal for specifier identifier.
        """

        if bundle_id_name is None:
            bundle_id_name = bundle_id_identifier.replace('.', ' ')

        self.printer.log_creating(BundleId, identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        try:
            bundle_id = self.api_client.bundle_ids.register(bundle_id_identifier, bundle_id_name, platform)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.printer.print_resource(bundle_id, should_print)
        self.printer.log_created(bundle_id)
        return bundle_id

    @cli.action('list-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM)
    def list_bundle_ids(self,
                        bundle_id_identifier: Optional[str] = None,
                        bundle_id_name: Optional[str] = None,
                        platform: BundleIdPlatform = BundleIdPlatform.IOS,
                        should_print: bool = True) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints.
        """

        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        bundle_ids = self._list_resources(bundle_id_filter, self.api_client.bundle_ids, should_print)

        return bundle_ids

    @cli.action('find-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.PLATFORM)
    def find_bundle_ids(self,
                        bundle_id_identifier: str,
                        platform: BundleIdPlatform = BundleIdPlatform.IOS,
                        should_print: bool = True) -> List[BundleId]:
        """
        Find Bundle IDs from Apple Developer portal for specified identifier.
        """

        bundle_ids = self.list_bundle_ids(
            bundle_id_identifier=bundle_id_identifier,
            platform=platform,
            should_print=False)

        self.printer.print_resources(bundle_ids, should_print)
        return bundle_ids

    @cli.action('get-bundle-id', BundleIdArgument.BUNDLE_ID_RESOURCE_ID)
    def get_bundle_id(self,
                      bundle_id_resource_id: ResourceId,
                      should_print: bool = True) -> BundleId:
        """
        Get specified Bundle ID from Apple Developer portal.
        """

        self.printer.log_get(BundleId, bundle_id_resource_id)
        try:
            bundle_id = self.api_client.bundle_ids.read(bundle_id_resource_id)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.printer.print_resource(bundle_id, should_print)
        return bundle_id

    @cli.action('delete-bundle-id',
                BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_bundle_id(self,
                         bundle_id_resource_id: ResourceId,
                         ignore_not_found: bool = False) -> None:
        """
        Delete specified Bundle ID from Apple Developer portal.
        """

        self._delete_resource(self.api_client.bundle_ids, bundle_id_resource_id, ignore_not_found)

    @classmethod
    def _get_certificate_private_key(cls,
                                     certificate_key: Optional[Types.CertificateKeyArgument],
                                     certificate_key_path: Optional[Types.CertificateKeyPathArgument],
                                     certificate_password: Optional[Types.CertificateKeyPasswordArgument]
                                     ) -> Optional[RSAPrivateKeyWithSerialization]:
        if certificate_key and certificate_key_path:
            private_key_arg = Colors.CYAN(CertificateArgument.PRIVATE_KEY.key.upper())
            private_key_path_arg = Colors.CYAN(CertificateArgument.PRIVATE_KEY_PATH.key.upper())
            raise AutomaticProvisioningError(f'Only one of {private_key_arg} and {private_key_path_arg} allowed')

        password = certificate_password.value if certificate_password else None
        if certificate_key:
            pem = certificate_key.value
            return models.PrivateKey.pem_to_rsa(pem, password)
        elif certificate_key_path:
            pem = certificate_key_path.value.expanduser().read_text()
            return models.PrivateKey.pem_to_rsa(pem, password)
        return None

    def _save_profile(self, profile: Profile) -> pathlib.Path:
        profile_path = self._get_unique_path(f'{profile.get_display_info()}.p12', self.profiles_directory)
        profile_path.write_bytes(profile.profile_content)
        self.printer.log_saved(profile, profile_path)
        return profile_path

    def _save_certificate(self,
                          certificate: Certificate,
                          rsa_key: RSAPrivateKeyWithSerialization,
                          p12_container_password: str) -> pathlib.Path:
        def command_runner(command_args: Tuple[str, ...],
                           obfuscate_patterns: Optional[Sequence[ObfuscationPattern]] = None):
            process = self.execute(command_args, obfuscate_patterns=obfuscate_patterns)
            if process.returncode == 0:
                return
            if 'unable to load private key' in process.stderr:
                error = 'Unable to export certificate: Invalid private key'
            else:
                error = 'Unable to export certificate: Failed to create PKCS12 container'
            raise AutomaticProvisioningError(error, process)

        certificate_path = self._get_unique_path(f'{certificate.get_display_info()}.p12', self.certificates_directory)
        p12_path = models.Certificate.export_p12(
            models.Certificate.asn1_to_x509(certificate.asn1_content),
            rsa_key,
            p12_container_password,
            export_path=certificate_path,
            command_runner=command_runner)
        self.printer.log_saved(certificate, p12_path)
        return p12_path

    def _save_profiles(self, profiles: Sequence[Profile]) -> List[pathlib.Path]:
        return [self._save_profile(profile) for profile in profiles]

    def _save_certificates(self,
                           certificates: Sequence[Certificate],
                           rsa_key: RSAPrivateKeyWithSerialization,
                           p12_container_password: str) -> List[pathlib.Path]:
        return [self._save_certificate(certificate, rsa_key, p12_container_password) for certificate in certificates]

    @cli.action('create-certificate',
                CertificateArgument.CERTIFICATE_TYPE,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def create_certificate(self,
                           certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
                           certificate_key: Optional[Types.CertificateKeyArgument] = None,
                           certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                           certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                           p12_container_password: str = 'password',
                           save: bool = False,
                           should_print: bool = True) -> Certificate:
        """
        Create code signing certificates of given type
        """

        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if rsa_key is None:
            raise AutomaticProvisioningError('Cannot create resource without private key')
        self.printer.log_creating(Certificate, type=certificate_type)
        csr = models.Certificate.create_certificate_signing_request(rsa_key)
        csr_content = models.Certificate.get_certificate_signing_request_content(csr)
        certificate = self.api_client.certificates.create(certificate_type, csr_content)
        self.printer.print_resource(certificate, should_print)
        self.printer.log_created(certificate)
        if save:
            self._save_certificate(certificate, rsa_key, p12_container_password)
        return certificate

    @cli.action('get-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def get_certificate(self,
                        certificate_resource_id: ResourceId,
                        certificate_key: Optional[Types.CertificateKeyArgument] = None,
                        certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                        p12_container_password: str = 'password',
                        save: bool = False,
                        should_print: bool = True) -> Certificate:
        """
        Get specified Certificate from Apple Developer portal.
        """

        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if save and rsa_key is None:
            raise AutomaticProvisioningError('Cannot save resource without private key')
        else:
            assert rsa_key is not None

        self.printer.log_get(Certificate, certificate_resource_id)
        try:
            certificate = self.api_client.certificates.read(certificate_resource_id)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        self.printer.print_resource(certificate, should_print)
        if save:
            self._save_certificate(certificate, rsa_key, p12_container_password)
        return certificate

    @cli.action('delete-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_certificate(self,
                           certificate_resource_id: ResourceId,
                           ignore_not_found: bool = False) -> None:
        """
        Delete specified Certificate from Apple Developer portal.
        """

        self._delete_resource(self.api_client.certificates, certificate_resource_id, ignore_not_found)

    @cli.action('fetch-certificates',
                CertificateArgument.CERTIFICATE_TYPE,
                CertificateArgument.DISPLAY_NAME,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def fetch_certificates(self,
                           certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
                           display_name: Optional[str] = None,
                           certificate_key: Optional[Types.CertificateKeyArgument] = None,
                           certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                           certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                           p12_container_password: str = 'password',
                           save: bool = False,
                           should_print: bool = True) -> List[Certificate]:
        """
        Fetch code signing certificates from Apple Developer Portal for offline use
        """

        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if save and rsa_key is None:
            raise AutomaticProvisioningError('Cannot create or save resource without private key')
        else:
            assert rsa_key is not None  # Make mypy happy

        certificate_filter = self.api_client.certificates.Filter(
            certificate_type=certificate_type,
            display_name=display_name)
        certificates = self._list_resources(certificate_filter, self.api_client.certificates, should_print)

        if save:
            self._save_certificates(certificates, rsa_key, p12_container_password)
        return certificates

    @cli.action('create-profile',
                BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
                CertificateArgument.CERTIFICATE_RESOURCE_IDS,
                DeviceArgument.DEVICE_RESOURCE_IDS,
                ProfileArgument.PROFILE_TYPE,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.SAVE)
    def create_profile(self,
                       bundle_id_resource_id: ResourceId,
                       certificate_resource_ids: Sequence[ResourceId],
                       device_resource_ids: Sequence[ResourceId],
                       profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
                       profile_name: Optional[str] = None,
                       save: bool = False,
                       should_print: bool = True) -> Profile:
        """
        Create provisioning profile of given type
        """

        bundle_id = self.get_bundle_id(bundle_id_resource_id)
        if profile_name and profile_name is not None:
            name = profile_name
        elif not profile_name:
            raise AutomaticProvisioningError(f'"{profile_name}" is not valid')
        else:
            name = f'{bundle_id.attributes.name} {profile_type.value.lower()}'

        self.printer.log_creating(Profile, **{'type': profile_type, f'{BundleId}': bundle_id.id, 'name': name})

        profile = self.api_client.profiles.create(
            name, profile_type, bundle_id, certificates=certificate_resource_ids, devices=device_resource_ids)
        self.printer.print_resource(profile, should_print)
        self.printer.log_created(profile)
        if save:
            self._save_profile(profile)
        return profile

    @cli.action('fetch-profiles',
                ProfileArgument.PROFILE_TYPE,
                ProfileArgument.PROFILE_STATE,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.SAVE)
    def fetch_profiles(self,
                       profile_type: Optional[ProfileType] = None,
                       profile_state: Optional[ProfileState] = None,
                       profile_name: Optional[str] = None,
                       save: bool = False,
                       should_print: bool = True) -> List[Profile]:
        """
        Fetch provisioning profiles from Apple Developer Portal for offline use
        """
        profile_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name)
        profiles = self._list_resources(profile_filter, self.api_client.profiles, should_print)

        if save:
            self._save_profiles(profiles)
        return profiles

    def _find_bundle_id_profiles(self, resource_id: ResourceId, profiles_filter) -> List[Profile]:
        self.printer.log_get_related(Profile, BundleId, resource_id)
        try:
            profiles = self.api_client.bundle_ids.list_profiles(
                bundle_id=resource_id,
                resource_filter=profiles_filter)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))
        self.printer.log_found(Profile, profiles, profiles_filter, BundleId)
        return profiles

    @cli.action('fetch-bundle-id-profiles',
                BundleIdArgument.BUNDLE_ID_RESOURCE_IDS,
                ProfileArgument.PROFILE_TYPE,
                ProfileArgument.PROFILE_STATE,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.SAVE)
    def fetch_bundle_id_profiles(self,
                                 bundle_id_resource_ids: Sequence[ResourceId],
                                 profile_type: Optional[ProfileType] = None,
                                 profile_state: Optional[ProfileState] = None,
                                 profile_name: Optional[str] = None,
                                 save: bool = False,
                                 should_print: bool = True) -> List[Profile]:
        """
        Fetch provisioning profiles from Apple Developer Portal for specified Bundle IDs.
        """

        profiles_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name)

        profiles = []
        for resource_id in set(bundle_id_resource_ids):
            profiles.extend(self._find_bundle_id_profiles(resource_id, profiles_filter))

        self.printer.print_resources(profiles, should_print)
        if save:
            self._save_profiles(profiles)
        return profiles

    def _get_or_create_bundle_ids(
            self, bundle_id_identifier: str, platform: BundleIdPlatform, create_resource: bool) -> List[BundleId]:
        bundle_ids = self.find_bundle_ids(bundle_id_identifier, platform=platform, should_print=False)
        if not bundle_ids and not create_resource:
            raise AutomaticProvisioningError(f'Did not find {BundleId.s} with identifier {bundle_id_identifier}')
        else:
            bundle_id = self.create_bundle_id(bundle_id_identifier, platform=platform, should_print=False)
            bundle_ids = [bundle_id]
        return bundle_ids

    def _get_or_create_certificates(self,
                                    profile_type: ProfileType,
                                    create_resource: bool) -> List[Certificate]:
        certificate_type = CertificateType.from_profile_type(profile_type)
        certificates = self.fetch_certificates(certificate_type=certificate_type, should_print=False)
        if not certificates and not create_resource:
            raise AutomaticProvisioningError(f'Did not find {certificate_type} {Certificate.s}')
        else:
            certificate = self.create_certificate(certificate_type, should_print=False)
            certificates = [certificate]
        return certificates

    def _create_missing_profiles(self,
                                 bundle_ids_without_profiles: Sequence[BundleId],
                                 certificates: Sequence[Certificate],
                                 profile_type: ProfileType) -> Iterator[Profile]:
        if not bundle_ids_without_profiles:
            return []
        platform = bundle_ids_without_profiles[0].attributes.platform
        devices = self.list_devices(
            platform=platform, device_status=DeviceStatus.ENABLED, should_print=False)
        for bundle_id in bundle_ids_without_profiles:
            yield self.create_profile(
                bundle_id.id,
                [certificate.id for certificate in certificates],
                [device.id for device in devices],
                profile_type=profile_type,
                should_print=False
            )

    def _get_or_create_profiles(self,
                                bundle_ids: Sequence[BundleId],
                                certificates: Sequence[Certificate],
                                profile_type: ProfileType,
                                create_resource: bool):
        profiles = self.fetch_bundle_id_profiles([bid.id for bid in bundle_ids], profile_type=profile_type)
        profiles = [profile for profile in profiles if profile.has_certificates(certificates)]
        bundle_ids_without_profiles = [bundle_id for bundle_id in bundle_ids if not bundle_id.has_profile(profiles)]
        if bundle_ids_without_profiles and not create_resource:
            missing = ", ".join(f'"{bid.attributes.identifier}" [{bid.id}]' for bid in bundle_ids_without_profiles)
            raise AutomaticProvisioningError(f'Did not find {profile_type} {Profile.s} for {BundleId.s}: {missing}')
        profiles.extend(self._create_missing_profiles(
            bundle_ids_without_profiles, certificates, profile_type))
        return profiles

    @cli.action('fetch',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.PLATFORM,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                ProfileArgument.PROFILE_TYPE,
                CommonArgument.CREATE_RESOURCE)
    def fetch_signing_files(self,
                            bundle_id_identifier: str,
                            certificate_key: Optional[Types.CertificateKeyArgument] = None,
                            certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                            certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                            p12_container_password: str = 'password',
                            platform: BundleIdPlatform = BundleIdPlatform.IOS,
                            profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
                            create_resource: bool = False):
        """
        Fetch provisioning profiles and code signing certificates for Bundle ID with given
        identifier.
        """

        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if rsa_key is None:
            raise AutomaticProvisioningError(f'Cannot save {Certificate.s} without private key')

        bundle_ids = self._get_or_create_bundle_ids(bundle_id_identifier, platform, create_resource)
        certificates = self._get_or_create_certificates(profile_type, create_resource)
        profiles = self._get_or_create_profiles(bundle_ids, certificates, profile_type, create_resource)

        self._save_certificates(certificates, rsa_key, p12_container_password)
        self._save_profiles(profiles)
        return profiles, certificates


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
