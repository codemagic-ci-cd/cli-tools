#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
from typing import List, Union
from typing import Optional
from typing import Sequence
from typing import Tuple
import shlex

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


class AutomaticProvisioningError(cli.CliAppException):
    pass


@cli.common_arguments(
    AutomaticProvisioningArgument.LOG_REQUESTS,
    AutomaticProvisioningArgument.ISSUER_ID,
    AutomaticProvisioningArgument.KEY_IDENTIFIER,
    AutomaticProvisioningArgument.PRIVATE_KEY,
    AutomaticProvisioningArgument.PRIVATE_KEY_PATH,
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
                 **kwargs):
        super().__init__(**kwargs)
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
        )

    def _list_resources(self, resource_filter, resource_manager):
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        resource_name = resource_manager.managed_resource.resource_names()
        self.logger.info(f'Found {len(resources)} {resource_name} matching {resource_filter}')
        return resources

    @cli.action('list-devices',
                BundleIdArgument.PLATFORM,
                DeviceArgument.DEVICE_NAME,
                DeviceArgument.DEVICE_STATUS,
                CommonArgument.JSON_OUTPUT)
    def list_devices(self,
                     platform: Optional[BundleIdPlatform] = None,
                     device_name: Optional[str] = None,
                     device_status: Optional[DeviceStatus] = None,
                     json_output: Optional[bool] = False,
                     print_resources: bool = True) -> List[Device]:
        """
        List Devices from Apple Developer portal matching given constraints.
        """

        device_filter = self.api_client.devices.Filter(
            name=device_name, platform=platform, status=device_status)
        devices = self._list_resources(device_filter, self.api_client.devices)

        if print_resources:
            BundleId.print_resources(devices, json_output)
        return devices

    @cli.action('create-bundle-id',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM,
                CommonArgument.JSON_OUTPUT)
    def create_bundle_id(self,
                         bundle_id_identifier: str,
                         bundle_id_name: Optional[str] = None,
                         platform: BundleIdPlatform = BundleIdPlatform.IOS,
                         json_output: Optional[bool] = False,
                         print_resources: bool = True) -> BundleId:
        """
        Create Bundle ID in Apple Developer portal for specifier identifier.
        """

        if bundle_id_name is None:
            bundle_id_name = bundle_id_identifier.replace('.', ' ')
        self.logger.info(
            f'Creating new Bundle ID "{bundle_id_identifier}" with name "{bundle_id_name}" for platform {platform}')
        try:
            bundle_id = self.api_client.bundle_ids.register(bundle_id_identifier, bundle_id_name, platform)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))
        self.logger.info(f'Created Bundle ID {bundle_id.id}')

        if print_resources:
            bundle_id.print(json_output)
        return bundle_id

    @cli.action('list-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM,
                CommonArgument.JSON_OUTPUT)
    def list_bundle_ids(self,
                        bundle_id_identifier: Optional[str] = None,
                        bundle_id_name: Optional[str] = None,
                        platform: BundleIdPlatform = BundleIdPlatform.IOS,
                        json_output: Optional[bool] = False,
                        print_resources: bool = True) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints.
        """

        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        bundle_ids = self._list_resources(bundle_id_filter, self.api_client.bundle_ids)
        if not bundle_ids:
            error_message = f'Did not find any Bundle IDs matching specified filters: {bundle_id_filter}'
            raise AutomaticProvisioningError(error_message)

        if print_resources:
            BundleId.print_resources(bundle_ids, json_output)
        return bundle_ids

    @cli.action('find-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.PLATFORM,
                CommonArgument.CREATE_RESOURCE,
                CommonArgument.JSON_OUTPUT)
    def find_bundle_ids(self,
                        bundle_id_identifier: str,
                        platform: BundleIdPlatform = BundleIdPlatform.IOS,
                        create_resource: Optional[bool] = False,
                        json_output: Optional[bool] = False,
                        print_resource: bool = True) -> List[BundleId]:
        """
        Find Bundle IDs from Apple Developer portal for specified identifier.
        """

        try:
            bundle_ids = self.list_bundle_ids(
                bundle_id_identifier=bundle_id_identifier,
                platform=platform,
                json_output=json_output,
                print_resources=True)
        except AutomaticProvisioningError:
            if not create_resource:
                raise
            self.logger.info(f'Bundle ID for identifier {bundle_id_identifier} not found.')
            bundle_id = self.create_bundle_id(
                bundle_id_identifier, json_output=json_output, platform=platform, print_resources=False)
            bundle_ids = [bundle_id]

        if print_resource:
            BundleId.print_resources(bundle_ids, json_output)
        return bundle_ids

    @cli.action('get-bundle-id',
                BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
                CommonArgument.JSON_OUTPUT)
    def get_bundle_id(self,
                      bundle_id_resource_id: ResourceId,
                      json_output: Optional[bool] = False,
                      print_resource: bool = True) -> BundleId:
        """
        Get specified Bundle ID from Apple Developer portal.
        """
        self.logger.info(f'Get Bundle ID {bundle_id_resource_id}')
        try:
            bundle_id = self.api_client.bundle_ids.read(bundle_id_resource_id)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        if print_resource:
            bundle_id.print(json_output)
        return bundle_id

    @cli.action('delete-bundle-id',
                BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_bundle_id(self,
                         bundle_id_resource_id: ResourceId,
                         ignore_not_found: Optional[bool] = False) -> None:
        """
        Delete specified Bundle ID from Apple Developer portal.
        """
        self.logger.info(f'Delete Bundle ID {bundle_id_resource_id}')
        try:
            self.api_client.bundle_ids.delete(bundle_id_resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found and api_error.status_code == 404:
                self.logger.info(f'Bundle ID {bundle_id_resource_id} does not exist, did not delete.')
                return
            raise AutomaticProvisioningError(str(api_error))
        else:
            self.logger.info(f'Successfully deleted Bundle ID {bundle_id_resource_id}')

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

    @classmethod
    def _safe_filename(cls, filename: str) -> str:
        return re.sub(r'[^\w.]', '_', filename)

    def _save_profile(self, profile: Profile) -> pathlib.Path:
        profile_name = self._safe_filename(f'{profile.get_display_info()}.p12')
        profile_path = self._get_unique_path(profile_name, self.profiles_directory)
        profile_path.write_bytes(profile.profile_content)
        self.logger.info(f'Saved {profile.get_display_info()} to {shlex.quote(str(profile_path))}')
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

        certificate_name = self._safe_filename(f'{certificate.get_display_info()}.p12')
        certificate_path = self._get_unique_path(certificate_name, self.certificates_directory)
        p12_path = models.Certificate.export_p12(
            models.Certificate.asn1_to_x509(certificate.asn1_content),
            rsa_key,
            p12_container_password,
            export_path=certificate_path,
            command_runner=command_runner)
        self.logger.info(f'Saved {certificate.get_display_info()} to {p12_path}')
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
                CommonArgument.JSON_OUTPUT,
                CommonArgument.SAVE)
    def create_certificate(self,
                           certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
                           certificate_key: Optional[Types.CertificateKeyArgument] = None,
                           certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                           certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                           p12_container_password: str = 'password',
                           json_output: bool = False,
                           save: bool = False,
                           print_resources: bool = True) -> Certificate:
        """
        Fetch code signing certificates from Apple Developer Portal for offline use
        """
        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if rsa_key is None:
            raise AutomaticProvisioningError('Cannot create resource without private key')
        csr = models.Certificate.create_certificate_signing_request(rsa_key)
        csr_content = models.Certificate.get_certificate_signing_request_content(csr)
        certificate = self.api_client.certificates.create(certificate_type, csr_content)
        self.logger.info(f'Created {certificate.get_display_info()}')
        if print_resources:
            certificate.print(json_output)
        if save:
            self._save_certificate(certificate, rsa_key, p12_container_password)
        return certificate

    @cli.action('get-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.JSON_OUTPUT,
                CommonArgument.SAVE)
    def get_certificate(self,
                        certificate_resource_id: ResourceId,
                        certificate_key: Optional[Types.CertificateKeyArgument] = None,
                        certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                        p12_container_password: str = 'password',
                        json_output: bool = False,
                        save: bool = False,
                        print_resource: bool = True) -> Certificate:
        """
        Get specified Certificate from Apple Developer portal.
        """
        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if save and rsa_key is None:
            raise AutomaticProvisioningError('Cannot save resource without private key')
        else:
            assert rsa_key is not None

        self.logger.info(f'Get Certificate {certificate_resource_id}')
        try:
            certificate = self.api_client.certificates.read(certificate_resource_id)
        except AppStoreConnectApiError as api_error:
            raise AutomaticProvisioningError(str(api_error))

        if print_resource:
            certificate.print(json_output)
        if save:
            self._save_certificate(certificate, rsa_key, p12_container_password)
        return certificate

    @cli.action('delete-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_certificate(self,
                           certificate_resource_id: ResourceId,
                           ignore_not_found: Optional[bool] = False) -> None:
        """
        Delete specified Certificate from Apple Developer portal.
        """
        self.logger.info(f'Delete Certificate {certificate_resource_id}')
        try:
            self.api_client.certificates.revoke(certificate_resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found and api_error.status_code == 404:
                self.logger.info(f'Certificate {certificate_resource_id} does not exist, did not delete.')
                return
            raise AutomaticProvisioningError(str(api_error))
        else:
            self.logger.info(f'Successfully deleted Certificate {certificate_resource_id}')

    @cli.action('fetch-certificates',
                CertificateArgument.CERTIFICATE_TYPE,
                CertificateArgument.DISPLAY_NAME,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.CREATE_RESOURCE,
                CommonArgument.JSON_OUTPUT,
                CommonArgument.SAVE)
    def fetch_certificates(self,
                           certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
                           display_name: Optional[str] = None,
                           certificate_key: Optional[Types.CertificateKeyArgument] = None,
                           certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                           certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                           p12_container_password: str = 'password',
                           create_resource: bool = False,
                           json_output: bool = False,
                           save: bool = False,
                           print_resources: bool = True) -> List[Certificate]:
        """
        Fetch code signing certificates from Apple Developer Portal for offline use
        """
        rsa_key = self._get_certificate_private_key(certificate_key, certificate_key_path, certificate_key_password)
        if (save or create_resource) and rsa_key is None:
            raise AutomaticProvisioningError('Cannot create or save resource without private key')
        else:
            assert rsa_key is not None  # Make mypy happy

        certificate_filter = self.api_client.certificates.Filter(
            certificate_type=certificate_type,
            display_name=display_name)

        certificates = self._list_resources(certificate_filter, self.api_client.certificates)
        if not certificates and create_resource:
            self.logger.info(f'Certificate with type {certificate_type} not found.')
            certificate = self.create_certificate(
                certificate_type,
                certificate_key=certificate_key,
                certificate_key_path=certificate_key_path,
                certificate_key_password=certificate_key_password,
                print_resources=False,
                save=False)
            certificates = [certificate]

        if save:
            self._save_certificates(certificates, rsa_key, p12_container_password)
        if print_resources:
            Certificate.print_resources(certificates, json_output)
        return certificates

    @cli.action('fetch-profiles',
                ProfileArgument.PROFILE_TYPE,
                ProfileArgument.PROFILE_STATE,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.JSON_OUTPUT,
                CommonArgument.SAVE)
    def fetch_profiles(self,
                       profile_type: Optional[ProfileType] = None,
                       profile_state: Optional[ProfileState] = None,
                       profile_name: Optional[str] = None,
                       json_output: bool = False,
                       save: bool = False,
                       print_resources: bool = True) -> List[Profile]:
        """
        Fetch provisioning profiles from Apple Developer Portal for offline use
        """
        profile_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name)
        profiles = self._list_resources(profile_filter, self.api_client.profiles)

        if print_resources:
            Profile.print_resources(profiles, json_output)
        if save:
            self._save_profiles(profiles)
        return profiles

    @cli.action('fetch',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.PLATFORM,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PATH,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                ProfileArgument.PROFILE_TYPE,
                DeviceArgument.NO_AUTO_PROVISION,
                CommonArgument.CREATE_RESOURCE,
                CommonArgument.JSON_OUTPUT)
    def fetch_signing_files(self,
                            bundle_id_identifier: str,
                            certificate_key: Optional[Types.CertificateKeyArgument] = None,
                            certificate_key_path: Optional[Types.CertificateKeyPathArgument] = None,
                            certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                            p12_container_password: str = 'password',
                            platform: BundleIdPlatform = BundleIdPlatform.IOS,
                            profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
                            auto_provision: Optional[bool] = True,
                            create_resource: Optional[bool] = False,
                            json_output: bool = False):
        """
        Fetch provisioning profiles and code signing certificates for Bundle ID with given
        identifier.
        """

        bundle_ids = self.find_bundle_ids(
            bundle_id_identifier,
            platform=platform,
            create_resource=create_resource,
            json_output=json_output,
            print_resource=False)
        if not bundle_ids:
            raise AutomaticProvisioningError(f'Did not find Bundle ID with identifier {bundle_id_identifier}')
        certificate_type = CertificateType.from_profile_type(profile_type)
        certificates = self.fetch_certificates(
            certificate_type=certificate_type,
            certificate_key=certificate_key,
            certificate_key_path=certificate_key_path,
            certificate_key_password=certificate_key_password,
            p12_container_password=p12_container_password,
            create_resource=True,
            print_resources=False)
        profiles: List[Profile] = []  # TODO: fetch profiles
        if auto_provision:
            devices = self.list_devices(
                platform=platform, device_status=DeviceStatus.ENABLED, print_resources=False)
            # TODO: update profiles with new devices
            ...
        raise NotImplemented


if __name__ == '__main__':
    AutomaticProvisioning.invoke_cli()
