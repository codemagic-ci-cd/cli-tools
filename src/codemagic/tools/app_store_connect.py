#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import tempfile
import time
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import Device
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Colors
from codemagic.models import Certificate
from codemagic.models import PrivateKey
from codemagic.models import ProvisioningProfile
from ._app_store_connect.arguments import AppStoreConnectArgument
from ._app_store_connect.arguments import BundleIdArgument
from ._app_store_connect.arguments import CertificateArgument
from ._app_store_connect.arguments import CommonArgument
from ._app_store_connect.arguments import DeviceArgument
from ._app_store_connect.arguments import ProfileArgument
from ._app_store_connect.arguments import Types
from ._app_store_connect.resource_printer import ResourcePrinter


class AppStoreConnectError(cli.CliAppException):
    pass


def _get_certificate_key(
        certificate_key: Optional[Types.CertificateKeyArgument] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None) -> Optional[PrivateKey]:
    password = certificate_key_password.value if certificate_key_password else None
    if certificate_key is not None:
        try:
            return PrivateKey.from_pem(certificate_key.value, password)
        except ValueError:
            CertificateArgument.PRIVATE_KEY.raise_argument_error('Not a valid certificate private key')
    return None


@cli.common_arguments(*AppStoreConnectArgument)
class AppStoreConnect(cli.CliApp):
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
                 profiles_directory: pathlib.Path = ProvisioningProfile.DEFAULT_LOCATION,
                 certificates_directory: pathlib.Path = Certificate.DEFAULT_LOCATION,
                 **kwargs):
        super().__init__(**kwargs)
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory
        self.printer = ResourcePrinter(bool(json_output), self.echo)
        self.api_client = AppStoreConnectApiClient(key_identifier, issuer_id, private_key, log_requests=log_requests)

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> AppStoreConnect:
        key_identifier_argument = AppStoreConnectArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AppStoreConnectArgument.ISSUER_ID.from_args(cli_args)
        private_key_argument = AppStoreConnectArgument.PRIVATE_KEY.from_args(cli_args)
        if issuer_id_argument is None:
            raise AppStoreConnectArgument.ISSUER_ID.raise_argument_error()
        if key_identifier_argument is None:
            raise AppStoreConnectArgument.KEY_IDENTIFIER.raise_argument_error()
        if private_key_argument is None:
            raise AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error()

        return AppStoreConnect(
            issuer_id=issuer_id_argument.value,
            key_identifier=key_identifier_argument.value,
            private_key=private_key_argument.value,
            log_requests=cli_args.log_requests,
            json_output=cli_args.json_output,
            **cls._parent_class_kwargs(cli_args)
        )

    def _create_resource(self, resource_manager, should_print, **create_params):
        omit_keys = create_params.pop('omit_keys', tuple())
        self.printer.log_creating(
            resource_manager.resource_type,
            **{k: v for k, v in create_params.items() if k not in omit_keys}
        )
        try:
            resource = resource_manager.create(**create_params)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.print_resource(resource, should_print)
        self.printer.log_created(resource)
        return resource

    def _get_resource(self, resource_id, resource_manager, should_print):
        self.printer.log_get(resource_manager.resource_type, resource_id)
        try:
            resource = resource_manager.read(resource_id)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.print_resource(resource, should_print)
        return resource

    def _list_resources(self, resource_filter, resource_manager, should_print):
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_found(resource_manager.resource_type, resources, resource_filter)
        self.printer.print_resources(resources, should_print)
        return resources

    def _delete_resource(self, resource_manager, resource_id: ResourceId, ignore_not_found: bool):
        self.printer.log_delete(resource_manager.resource_type, resource_id)
        try:
            resource_manager.delete(resource_id)
            self.printer.log_deleted(resource_manager.resource_type, resource_id)
        except AppStoreConnectApiError as api_error:
            if ignore_not_found is True and api_error.status_code == 404:
                self.printer.log_ignore_not_deleted(resource_manager.resource_type, resource_id)
            else:
                raise AppStoreConnectError(str(api_error))

    @cli.action('list-devices',
                BundleIdArgument.PLATFORM_OPTIONAL,
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

        create_params = dict(identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        return self._create_resource(self.api_client.bundle_ids, should_print, **create_params)

    @cli.action('list-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM_OPTIONAL)
    def list_bundle_ids(self,
                        bundle_id_identifier: Optional[str] = None,
                        bundle_id_name: Optional[str] = None,
                        platform: Optional[BundleIdPlatform] = None,
                        should_print: bool = True) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints.
        """

        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        bundle_ids = self._list_resources(bundle_id_filter, self.api_client.bundle_ids, should_print)

        return bundle_ids

    @cli.action('get-bundle-id', BundleIdArgument.BUNDLE_ID_RESOURCE_ID)
    def get_bundle_id(self,
                      bundle_id_resource_id: ResourceId,
                      should_print: bool = True) -> BundleId:
        """
        Get specified Bundle ID from Apple Developer portal.
        """

        return self._get_resource(bundle_id_resource_id, self.api_client.bundle_ids, should_print)

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

    @cli.action('create-certificate',
                CertificateArgument.CERTIFICATE_TYPE,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def create_certificate(self,
                           certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
                           certificate_key: Optional[Types.CertificateKeyArgument] = None,
                           certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                           p12_container_password: str = '',
                           save: bool = False,
                           should_print: bool = True) -> SigningCertificate:
        """
        Create code signing certificates of given type
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if private_key is None:
            raise AppStoreConnectError('Cannot create resource without private key')

        csr = Certificate.create_certificate_signing_request(private_key)
        csr_content = Certificate.get_certificate_signing_request_content(csr)

        create_params = dict(csr_content=csr_content, certificate_type=certificate_type, omit_keys=['csr_content'])
        certificate = self._create_resource(self.api_client.signing_certificates, should_print, **create_params)

        if save:
            self._save_certificate(certificate, private_key, p12_container_password)
        return certificate

    @cli.action('get-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def get_certificate(self,
                        certificate_resource_id: ResourceId,
                        certificate_key: Optional[Types.CertificateKeyArgument] = None,
                        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                        p12_container_password: str = '',
                        save: bool = False,
                        should_print: bool = True) -> SigningCertificate:
        """
        Get specified Signing Certificate from Apple Developer portal.
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if save and private_key is None:
            raise AppStoreConnectError('Cannot save resource without private key')
        else:
            assert private_key is not None

        certificate = self._get_resource(certificate_resource_id, self.api_client.signing_certificates, should_print)

        if save:
            self._save_certificate(certificate, private_key, p12_container_password)
        return certificate

    @cli.action('delete-certificate',
                CertificateArgument.CERTIFICATE_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_certificate(self,
                           certificate_resource_id: ResourceId,
                           ignore_not_found: bool = False) -> None:
        """
        Delete specified Signing Certificate from Apple Developer portal.
        """

        self._delete_resource(self.api_client.signing_certificates, certificate_resource_id, ignore_not_found)

    @cli.action('list-certificates',
                CertificateArgument.CERTIFICATE_TYPE_OPTIONAL,
                CertificateArgument.DISPLAY_NAME,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def list_certificates(self,
                          certificate_type: Optional[CertificateType] = None,
                          display_name: Optional[str] = None,
                          certificate_key: Optional[Types.CertificateKeyArgument] = None,
                          certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                          p12_container_password: str = '',
                          save: bool = False,
                          should_print: bool = True) -> List[SigningCertificate]:
        """
        List Signing Certificates from Apple Developer Portal matching given constraints.
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if save and private_key is None:
            raise AppStoreConnectError('Cannot create or save resource without private key')

        certificate_filter = self.api_client.signing_certificates.Filter(
            certificate_type=certificate_type,
            display_name=display_name)
        certificates = self._list_resources(certificate_filter, self.api_client.signing_certificates, should_print)

        if private_key:
            certificates = [
                certificate for certificate in certificates
                if Certificate.from_ans1(certificate.asn1_content).is_signed_with(private_key)
            ]
            self.printer.log_filtered(SigningCertificate, certificates, 'for given private key')

        if save:
            assert private_key is not None  # Make mypy happy
            self._save_certificates(certificates, private_key, p12_container_password)

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

        bundle_id = self.get_bundle_id(bundle_id_resource_id, should_print=False)
        if profile_name:
            name = profile_name
        elif profile_name is None:
            name = f'{bundle_id.attributes.name} {profile_type.value.lower()} {int(time.time())}'
        else:
            raise AppStoreConnectError(f'"{profile_name}" is not a valid {Profile} name')

        create_params = dict(
            name=name,
            profile_type=profile_type,
            bundle_id=bundle_id_resource_id,
            certificates=certificate_resource_ids,
            devices=[],
            omit_keys=['devices']
        )
        if profile_type.devices_allowed():
            create_params['devices'] = device_resource_ids
        profile = self._create_resource(self.api_client.profiles, should_print, **create_params)

        if save:
            self._save_profile(profile)
        return profile

    @cli.action('get-profile', ProfileArgument.PROFILE_RESOURCE_ID)
    def get_profile(self, profile_resource_id: ResourceId, should_print: bool = True) -> Profile:
        """
        Get specified Profile from Apple Developer portal.
        """

        return self._get_resource(profile_resource_id, self.api_client.profiles, should_print)

    @cli.action('delete-profile',
                ProfileArgument.PROFILE_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_profile(self,
                       profile_resource_id: ResourceId,
                       ignore_not_found: bool = False) -> None:
        """
        Delete specified Profile from Apple Developer portal.
        """

        self._delete_resource(self.api_client.profiles, profile_resource_id, ignore_not_found)

    @cli.action('list-profiles',
                ProfileArgument.PROFILE_TYPE_OPTIONAL,
                ProfileArgument.PROFILE_STATE_OPTIONAL,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.SAVE)
    def list_profiles(self,
                      profile_type: Optional[ProfileType] = None,
                      profile_state: Optional[ProfileState] = None,
                      profile_name: Optional[str] = None,
                      save: bool = False,
                      should_print: bool = True) -> List[Profile]:
        """
        List Profiles from Apple Developer portal matching given constraints.
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
            raise AppStoreConnectError(str(api_error))
        self.printer.log_found(Profile, profiles, profiles_filter, BundleId)
        return profiles

    @cli.action('list-bundle-id-profiles',
                BundleIdArgument.BUNDLE_ID_RESOURCE_IDS,
                ProfileArgument.PROFILE_TYPE_OPTIONAL,
                ProfileArgument.PROFILE_STATE_OPTIONAL,
                ProfileArgument.PROFILE_NAME,
                CommonArgument.SAVE)
    def list_bundle_id_profiles(self,
                                bundle_id_resource_ids: Sequence[ResourceId],
                                profile_type: Optional[ProfileType] = None,
                                profile_state: Optional[ProfileState] = None,
                                profile_name: Optional[str] = None,
                                save: bool = False,
                                should_print: bool = True) -> List[Profile]:
        """
        List provisioning profiles from Apple Developer Portal for specified Bundle IDs.
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

    @cli.action('fetch-signing-files',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER,
                BundleIdArgument.PLATFORM,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                ProfileArgument.PROFILE_TYPE,
                CommonArgument.CREATE_RESOURCE)
    def fetch_signing_files(self,
                            bundle_id_identifier: str,
                            certificate_key: Optional[Types.CertificateKeyArgument] = None,
                            certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                            p12_container_password: str = '',
                            platform: BundleIdPlatform = BundleIdPlatform.IOS,
                            profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
                            create_resource: bool = False) -> Tuple[List[Profile], List[SigningCertificate]]:
        """
        Fetch provisioning profiles and code signing certificates
        for Bundle ID with given identifier.
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if private_key is None:
            raise AppStoreConnectError(f'Cannot save {SigningCertificate.s} without private key')

        bundle_ids = self._get_or_create_bundle_ids(bundle_id_identifier, platform, create_resource)
        certificates = self._get_or_create_certificates(
            profile_type, certificate_key, certificate_key_password, create_resource)
        profiles = self._get_or_create_profiles(bundle_ids, certificates, profile_type, create_resource)

        self._save_certificates(certificates, private_key, p12_container_password)
        self._save_profiles(profiles)
        return profiles, certificates

    def _get_or_create_bundle_ids(
            self, bundle_id_identifier: str, platform: BundleIdPlatform, create_resource: bool) -> List[BundleId]:
        bundle_ids = self.list_bundle_ids(bundle_id_identifier, platform=platform, should_print=False)
        if not bundle_ids:
            if not create_resource:
                raise AppStoreConnectError(f'Did not find {BundleId.s} with identifier {bundle_id_identifier}')
            bundle_ids.append(self.create_bundle_id(bundle_id_identifier, platform=platform, should_print=False))
        return bundle_ids

    def _get_or_create_certificates(self,
                                    profile_type: ProfileType,
                                    certificate_key: Optional[Types.CertificateKeyArgument],
                                    certificate_key_password: Optional[Types.CertificateKeyPasswordArgument],
                                    create_resource: bool) -> List[SigningCertificate]:
        certificate_type = CertificateType.from_profile_type(profile_type)
        certificates = self.list_certificates(
            certificate_type=certificate_type,
            certificate_key=certificate_key,
            certificate_key_password=certificate_key_password,
            should_print=False)

        if not certificates:
            if not create_resource:
                raise AppStoreConnectError(f'Did not find {certificate_type} {SigningCertificate.s}')
            certificates.append(self.create_certificate(
                certificate_type,
                certificate_key=certificate_key,
                certificate_key_password=certificate_key_password,
                should_print=False))
        return certificates

    def _create_missing_profiles(self,
                                 bundle_ids_without_profiles: Sequence[BundleId],
                                 certificates: Sequence[SigningCertificate],
                                 profile_type: ProfileType) -> Iterator[Profile]:
        if not bundle_ids_without_profiles:
            return []
        platform = bundle_ids_without_profiles[0].attributes.platform
        devices = self.list_devices(platform=platform, device_status=DeviceStatus.ENABLED, should_print=False)
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
                                certificates: Sequence[SigningCertificate],
                                profile_type: ProfileType,
                                create_resource: bool):
        def has_certificate(profile) -> bool:
            try:
                profile_certificates = self.api_client.profiles.list_certificate_ids(profile)
                return bool(certificate_ids.issubset({c.id for c in profile_certificates}))
            except AppStoreConnectApiError as err:
                error = f'Listing {SigningCertificate.s} for {Profile} {profile.id} failed unexpectedly'
                self.logger.warning(Colors.YELLOW(f'{error}: {err.error_response}'))
                return False

        def missing_profile(bundle_id) -> bool:
            try:
                bundle_ids_profiles = self.api_client.bundle_ids.list_profile_ids(bundle_id)
                return not (profile_ids & {p.id for p in bundle_ids_profiles})
            except AppStoreConnectApiError as err:
                error = f'Listing {Profile.s} for {BundleId} {bundle_id.id} failed unexpectedly'
                self.logger.warning(Colors.YELLOW(f'{error}: {err.error_response}'))
                return True

        certificate_ids = {c.id for c in certificates}
        profiles = self.list_bundle_id_profiles(
            [bundle_id.id for bundle_id in bundle_ids],
            profile_type=profile_type,
            profile_state=ProfileState.ACTIVE,
            should_print=False)
        profiles = list(filter(has_certificate, profiles))

        certificate_names = (f'{c.attributes.displayName} [{c.attributes.serialNumber}]' for c in certificates)
        message = f'that contain certificate(s) {", ".join(certificate_names)}'
        self.printer.log_filtered(Profile, profiles, message)

        profile_ids = {p.id for p in profiles}
        bundle_ids_without_profiles = list(filter(missing_profile, bundle_ids))
        if bundle_ids_without_profiles and not create_resource:
            missing = ", ".join(f'"{bid.attributes.identifier}" [{bid.id}]' for bid in bundle_ids_without_profiles)
            raise AppStoreConnectError(f'Did not find {profile_type} {Profile.s} for {BundleId.s}: {missing}')

        created_profiles = self._create_missing_profiles(bundle_ids_without_profiles, certificates, profile_type)
        profiles.extend(created_profiles)
        return profiles

    @classmethod
    def _get_unique_path(cls, file_name: str, destination: pathlib.Path) -> pathlib.Path:
        if destination.exists() and not destination.is_dir():
            raise ValueError(f'Destination {destination} is not a directory')
        destination.mkdir(parents=True, exist_ok=True)
        name = pathlib.Path(re.sub(r'[^\w.]', '_', file_name))
        tf = tempfile.NamedTemporaryFile(
            prefix=f'{name.stem}_', suffix=name.suffix, dir=destination, delete=False)
        tf.close()
        return pathlib.Path(tf.name)

    def _save_profile(self, profile: Profile) -> pathlib.Path:
        profile_path = self._get_unique_path(f'{profile.get_display_info()}.mobileprovision', self.profiles_directory)
        profile_path.write_bytes(profile.profile_content)
        self.printer.log_saved(profile, profile_path)
        return profile_path

    def _save_certificate(self,
                          certificate: SigningCertificate,
                          private_key: PrivateKey,
                          p12_container_password: str) -> pathlib.Path:
        certificate_path = self._get_unique_path(f'{certificate.get_display_info()}.p12', self.certificates_directory)
        try:
            p12_path = Certificate.from_ans1(certificate.asn1_content).export_p12(
                private_key,
                p12_container_password,
                export_path=certificate_path,
                cli_app=self)
        except (ValueError, IOError) as error:
            raise AppStoreConnectError(*error.args)
        self.printer.log_saved(certificate, p12_path)
        return p12_path

    def _save_profiles(self, profiles: Sequence[Profile]) -> List[pathlib.Path]:
        return [self._save_profile(profile) for profile in profiles]

    def _save_certificates(self,
                           certificates: Sequence[SigningCertificate],
                           private_key: PrivateKey,
                           p12_container_password: str) -> List[pathlib.Path]:
        return [self._save_certificate(c, private_key, p12_container_password) for c in certificates]


if __name__ == '__main__':
    AppStoreConnect.invoke_cli()
