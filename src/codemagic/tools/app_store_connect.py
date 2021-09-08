#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import tempfile
import time
from distutils.version import LooseVersion
from functools import lru_cache
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
from codemagic.apple.resources import AppStoreVersionSubmission
from codemagic.apple.resources import Build
from codemagic.apple.resources import BuildProcessingState
from codemagic.apple.resources import BundleId
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import Device
from codemagic.apple.resources import DeviceStatus
from codemagic.apple.resources import Platform
from codemagic.apple.resources import Profile
from codemagic.apple.resources import ProfileState
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import Certificate
from codemagic.models import PrivateKey
from codemagic.models import ProvisioningProfile

from ._app_store_connect.action_group import AppStoreConnectActionGroup
from ._app_store_connect.action_groups import AppsActionGroup
from ._app_store_connect.action_groups import BetaAppReviewSubmissionsActionGroup
from ._app_store_connect.action_groups import BetaBuildLocalizationsActionGroup
from ._app_store_connect.action_groups import BetaGroupsActionGroup
from ._app_store_connect.action_groups import BuildsActionGroup
from ._app_store_connect.actions import PublishAction
from ._app_store_connect.arguments import AppArgument
from ._app_store_connect.arguments import AppStoreConnectArgument
from ._app_store_connect.arguments import AppStoreVersionArgument
from ._app_store_connect.arguments import BetaBuildInfo  # noqa: F401
from ._app_store_connect.arguments import BuildArgument
from ._app_store_connect.arguments import BundleIdArgument
from ._app_store_connect.arguments import CertificateArgument
from ._app_store_connect.arguments import CommonArgument
from ._app_store_connect.arguments import DeviceArgument
from ._app_store_connect.arguments import ProfileArgument
from ._app_store_connect.arguments import PublishArgument  # noqa: F401
from ._app_store_connect.arguments import Types
from ._app_store_connect.errors import AppStoreConnectError
from ._app_store_connect.resource_manager_mixin import ResourceManagerMixin
from ._app_store_connect.resource_printer import ResourcePrinter


def _get_certificate_key(
        certificate_key: Optional[Types.CertificateKeyArgument] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None) -> Optional[PrivateKey]:
    password = certificate_key_password.value if certificate_key_password else None
    if certificate_key is not None:
        try:
            return PrivateKey.from_buffer(certificate_key.value, password)
        except ValueError:
            CertificateArgument.PRIVATE_KEY.raise_argument_error('Not a valid certificate private key')
    return None


@cli.common_arguments(*AppStoreConnectArgument)
class AppStoreConnect(cli.CliApp,
                      PublishAction,
                      AppsActionGroup,
                      BuildsActionGroup,
                      BetaAppReviewSubmissionsActionGroup,
                      BetaBuildLocalizationsActionGroup,
                      BetaGroupsActionGroup,
                      ResourceManagerMixin,
                      PathFinderMixin):
    """
    Interact with Apple services via App Store Connect API
    """

    def __init__(self,
                 key_identifier: Optional[KeyIdentifier],
                 issuer_id: Optional[IssuerId],
                 private_key: Optional[str],
                 log_requests: bool = False,
                 json_output: bool = False,
                 profiles_directory: pathlib.Path = ProvisioningProfile.DEFAULT_LOCATION,
                 certificates_directory: pathlib.Path = Certificate.DEFAULT_LOCATION,
                 **kwargs):
        super().__init__(**kwargs)
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory
        self.printer = ResourcePrinter(bool(json_output), self.echo)
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._log_requests = log_requests

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> AppStoreConnect:
        key_identifier_argument = AppStoreConnectArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AppStoreConnectArgument.ISSUER_ID.from_args(cli_args)
        private_key_argument = AppStoreConnectArgument.PRIVATE_KEY.from_args(cli_args)

        app_store_connect = AppStoreConnect(
            key_identifier=key_identifier_argument.value if key_identifier_argument else None,
            issuer_id=issuer_id_argument.value if issuer_id_argument else None,
            private_key=private_key_argument.value if private_key_argument else None,
            log_requests=cli_args.log_requests,
            json_output=cli_args.json_output,
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            **cls._parent_class_kwargs(cli_args),
        )

        cli_action = app_store_connect._get_invoked_cli_action(cli_args)
        if cli_action.action_options.get('requires_api_client', True):
            app_store_connect._assert_api_client_credentials()

        return app_store_connect

    def _assert_api_client_credentials(self, custom_error: Optional[str] = None):
        if self._issuer_id is None:
            if custom_error:
                default_message = AppStoreConnectArgument.ISSUER_ID.get_missing_value_error_message()
                raise AppStoreConnectArgument.ISSUER_ID.raise_argument_error(f'{default_message}. {custom_error}')
            else:
                raise AppStoreConnectArgument.ISSUER_ID.raise_argument_error()

        if self._key_identifier is None:
            if custom_error:
                default_message = AppStoreConnectArgument.KEY_IDENTIFIER.get_missing_value_error_message()
                raise AppStoreConnectArgument.KEY_IDENTIFIER.raise_argument_error(f'{default_message}. {custom_error}')
            else:
                raise AppStoreConnectArgument.KEY_IDENTIFIER.raise_argument_error()

        try:
            self._resolve_app_store_connect_private_key()
        except ValueError as ve:
            custom_error = ve.args[0] if ve.args else custom_error
            if custom_error:
                default_message = AppStoreConnectArgument.PRIVATE_KEY.get_missing_value_error_message()
                AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error(f'{default_message}. {custom_error}')
            else:
                AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error()

    def _resolve_app_store_connect_private_key(self):
        if self._private_key is not None:
            return

        for keys_path in Types.PrivateKeyArgument.PRIVATE_KEY_LOCATIONS:
            try:
                api_key = next(keys_path.expanduser().glob(f'AuthKey_{self._key_identifier}.p8'))
            except StopIteration:
                continue

            try:
                private_key_argument = Types.PrivateKeyArgument(api_key.read_text())
            except ValueError:
                raise ValueError(f'Provided value in {api_key} is not valid')
            self._private_key = private_key_argument.value
            break
        else:
            raise ValueError()

    @lru_cache(1)
    def _get_api_client(self) -> AppStoreConnectApiClient:
        assert self._key_identifier is not None
        assert self._issuer_id is not None
        assert self._private_key is not None
        return AppStoreConnectApiClient(
            self._key_identifier,
            self._issuer_id,
            self._private_key,
            log_requests=self._log_requests,
        )

    @property
    def api_client(self) -> AppStoreConnectApiClient:
        return self._get_api_client()

    @cli.action('list-builds',
                AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
                BuildArgument.EXPIRED,
                BuildArgument.NOT_EXPIRED,
                BuildArgument.BUILD_ID_RESOURCE_ID_OPTIONAL,
                BuildArgument.PRE_RELEASE_VERSION,
                BuildArgument.PROCESSING_STATE,
                BuildArgument.BUILD_VERSION_NUMBER)
    def list_builds(self,
                    application_id: Optional[ResourceId] = None,
                    expired: Optional[bool] = None,
                    not_expired: Optional[bool] = None,
                    build_id: Optional[ResourceId] = None,
                    pre_release_version: Optional[str] = None,
                    processing_state: Optional[BuildProcessingState] = None,
                    build_version_number: Optional[int] = None,
                    should_print: bool = True) -> List[Build]:
        """
        List Builds from Apple Developer Portal matching given constraints
        """
        try:
            expired_value = Argument.resolve_optional_two_way_switch(expired, not_expired)
        except ValueError:
            flags = f'{BuildArgument.EXPIRED.flags!r} and {BuildArgument.NOT_EXPIRED.flags!r}'
            raise BuildArgument.NOT_EXPIRED.raise_argument_error(f'Using mutually exclusive switches {flags}.')

        builds_filter = self.api_client.builds.Filter(
            app=application_id,
            expired=expired_value,
            id=build_id,
            processing_state=processing_state,
            version=build_version_number,
            pre_release_version_version=pre_release_version,
        )
        return self._list_resources(builds_filter, self.api_client.builds, should_print)

    @classmethod
    def _get_latest_build_number(cls, builds: List[Build]) -> Optional[str]:
        if not builds:
            return None
        most_recent_build = max(builds, key=lambda b: LooseVersion(b.attributes.version))
        version = most_recent_build.attributes.version
        cls.echo(version)
        return version

    @cli.action('get-latest-app-store-build-number',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                AppStoreVersionArgument.VERSION_STRING,
                CommonArgument.PLATFORM)
    def get_latest_app_store_build_number(self,
                                          application_id: ResourceId,
                                          version_string: Optional[str] = None,
                                          platform: Optional[Platform] = None,
                                          should_print: bool = False) -> Optional[str]:
        """
        Get latest App Store build number for the given application
        """
        versions_client = self.api_client.app_store_versions
        versions_filter = versions_client.Filter(version_string=version_string, platform=platform)
        try:
            _versions, builds = versions_client.list_with_include(
                application_id, Build, resource_filter=versions_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.log_found(Build, builds, versions_filter)
        self.printer.print_resources(builds, should_print)
        return self._get_latest_build_number(builds)

    @cli.action('get-latest-testflight-build-number',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                BuildArgument.PRE_RELEASE_VERSION,
                CommonArgument.PLATFORM)
    def get_latest_testflight_build_number(self,
                                           application_id: ResourceId,
                                           pre_release_version: Optional[str] = None,
                                           platform: Optional[Platform] = None,
                                           should_print: bool = False) -> Optional[str]:
        """
        Get latest Testflight build number for the given application
        """
        versions_client = self.api_client.pre_release_versions
        versions_filter = versions_client.Filter(app=application_id, platform=platform, version=pre_release_version)
        try:
            _versions, builds = versions_client.list_with_include(Build, resource_filter=versions_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))
        self.printer.log_found(Build, builds, versions_filter)
        self.printer.print_resources(builds, should_print)
        return self._get_latest_build_number(builds)

    @cli.action('list-devices',
                BundleIdArgument.PLATFORM_OPTIONAL,
                DeviceArgument.DEVICE_NAME_OPTIONAL,
                DeviceArgument.DEVICE_STATUS)
    def list_devices(self,
                     platform: Optional[BundleIdPlatform] = None,
                     device_name: Optional[str] = None,
                     device_status: Optional[DeviceStatus] = None,
                     should_print: bool = True) -> List[Device]:
        """
        List Devices from Apple Developer portal matching given constraints
        """

        device_filter = self.api_client.devices.Filter(
            name=device_name, platform=platform, status=device_status)
        return self._list_resources(device_filter, self.api_client.devices, should_print)

    @cli.action('register-device',
                BundleIdArgument.PLATFORM,
                DeviceArgument.DEVICE_NAME,
                DeviceArgument.DEVICE_UDID)
    def register_device(
        self,
        platform: BundleIdPlatform,
        device_name: str,
        device_udid: str,
        should_print: bool = True,
    ) -> Device:
        """
        Register a new device for app development
        """
        return self._create_resource(
            self.api_client.devices,
            should_print,
            udid=device_udid,
            name=device_name,
            platform=platform,
        )

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
        Create Bundle ID in Apple Developer portal for specifier identifier
        """

        if bundle_id_name is None:
            bundle_id_name = bundle_id_identifier.replace('.', ' ')

        create_params = dict(identifier=bundle_id_identifier, name=bundle_id_name, platform=platform)
        return self._create_resource(self.api_client.bundle_ids, should_print, **create_params)

    @cli.action('list-bundle-ids',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                BundleIdArgument.BUNDLE_ID_NAME,
                BundleIdArgument.PLATFORM_OPTIONAL,
                BundleIdArgument.IDENTIFIER_STRICT_MATCH)
    def list_bundle_ids(self,
                        bundle_id_identifier: Optional[str] = None,
                        bundle_id_name: Optional[str] = None,
                        platform: Optional[BundleIdPlatform] = None,
                        bundle_id_identifier_strict_match: bool = False,
                        should_print: bool = True) -> List[BundleId]:
        """
        List Bundle IDs from Apple Developer portal matching given constraints
        """

        def predicate(bundle_id):
            return bundle_id.attributes.identifier == bundle_id_identifier

        bundle_id_filter = self.api_client.bundle_ids.Filter(
            identifier=bundle_id_identifier,
            name=bundle_id_name,
            platform=platform,
        )
        bundle_ids = self._list_resources(
            bundle_id_filter,
            self.api_client.bundle_ids,
            should_print,
            filter_predicate=predicate if bundle_id_identifier_strict_match else None,
        )

        return bundle_ids

    @cli.action('get-bundle-id', BundleIdArgument.BUNDLE_ID_RESOURCE_ID)
    def get_bundle_id(self,
                      bundle_id_resource_id: ResourceId,
                      should_print: bool = True) -> BundleId:
        """
        Get specified Bundle ID from Apple Developer portal
        """

        return self._get_resource(bundle_id_resource_id, self.api_client.bundle_ids, should_print)

    @cli.action('delete-bundle-id',
                BundleIdArgument.BUNDLE_ID_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_bundle_id(self,
                         bundle_id_resource_id: ResourceId,
                         ignore_not_found: bool = False) -> None:
        """
        Delete specified Bundle ID from Apple Developer portal
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
            raise AppStoreConnectError('Cannot create resource without certificate private key')

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
        Get specified Signing Certificate from Apple Developer portal
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if save and private_key is None:
            raise AppStoreConnectError('Cannot save resource without certificate private key')
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
        Delete specified Signing Certificate from Apple Developer portal
        """

        self._delete_resource(self.api_client.signing_certificates, certificate_resource_id, ignore_not_found)

    @cli.action('list-certificates',
                CertificateArgument.CERTIFICATE_TYPE_OPTIONAL,
                CertificateArgument.PROFILE_TYPE_OPTIONAL,
                CertificateArgument.DISPLAY_NAME,
                CertificateArgument.PRIVATE_KEY,
                CertificateArgument.PRIVATE_KEY_PASSWORD,
                CertificateArgument.P12_CONTAINER_PASSWORD,
                CommonArgument.SAVE)
    def list_certificates(self,
                          certificate_type: Optional[CertificateType] = None,
                          profile_type: Optional[ProfileType] = None,
                          display_name: Optional[str] = None,
                          certificate_key: Optional[Types.CertificateKeyArgument] = None,
                          certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                          p12_container_password: str = '',
                          save: bool = False,
                          should_print: bool = True) -> List[SigningCertificate]:
        """
        List Signing Certificates from Apple Developer Portal matching given constraints
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if save and private_key is None:
            raise AppStoreConnectError('Cannot create or save resource without certificate private key')

        if profile_type:
            certificate_type = CertificateType.from_profile_type(profile_type)

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

    @cli.action('create',
                AppStoreVersionArgument.APP_STORE_VERSION_ID,
                action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_SUBMISSIONS)
    def create_app_store_version_submission(self,
                                            app_store_version_id: ResourceId,
                                            should_print: bool = True) -> AppStoreVersionSubmission:
        """
        Submit an App Store Version to App Review
        """
        return self._create_resource(
            self.api_client.app_store_version_submissions,
            should_print,
            app_store_version=app_store_version_id,
        )

    @cli.action('delete',
                AppStoreVersionArgument.APP_STORE_VERSION_SUBMISSION_ID,
                CommonArgument.IGNORE_NOT_FOUND,
                action_group=AppStoreConnectActionGroup.APP_STORE_VERSION_SUBMISSIONS)
    def delete_app_store_version_submission(self,
                                            app_store_version_submission_id: ResourceId,
                                            ignore_not_found: bool = False) -> None:
        """
        Remove a version submission from App Store review
        """
        self._delete_resource(
            self.api_client.app_store_version_submissions,
            app_store_version_submission_id,
            ignore_not_found=ignore_not_found,
        )

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
            omit_keys=['devices'],
        )
        if profile_type.devices_allowed():
            create_params['devices'] = device_resource_ids
        profile = self._create_resource(self.api_client.profiles, should_print, **create_params)

        if save:
            self._save_profile(profile)
        return profile

    @cli.action('get-profile',
                ProfileArgument.PROFILE_RESOURCE_ID,
                CommonArgument.SAVE)
    def get_profile(self,
                    profile_resource_id: ResourceId,
                    save: bool = False,
                    should_print: bool = True) -> Profile:
        """
        Get specified Profile from Apple Developer portal
        """

        profile = self._get_resource(profile_resource_id, self.api_client.profiles, should_print)
        if save:
            self._save_profile(profile)
        return profile

    @cli.action('delete-profile',
                ProfileArgument.PROFILE_RESOURCE_ID,
                CommonArgument.IGNORE_NOT_FOUND)
    def delete_profile(self,
                       profile_resource_id: ResourceId,
                       ignore_not_found: bool = False) -> None:
        """
        Delete specified Profile from Apple Developer portal
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
        List Profiles from Apple Developer portal matching given constraints
        """
        profile_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name)
        profiles = self._list_resources(profile_filter, self.api_client.profiles, should_print)

        if save:
            self._save_profiles(profiles)
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
        List provisioning profiles from Apple Developer Portal for specified Bundle IDs
        """

        profiles_filter = self.api_client.profiles.Filter(
            profile_type=profile_type,
            profile_state=profile_state,
            name=profile_name)

        profiles = []
        for resource_id in set(bundle_id_resource_ids):
            bundle_id_profiles = self._list_related_resources(
                resource_id,
                BundleId,
                Profile,
                self.api_client.bundle_ids.list_profiles,
                profiles_filter,
                should_print,
            )
            profiles.extend(bundle_id_profiles)

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
                BundleIdArgument.IDENTIFIER_STRICT_MATCH,
                CommonArgument.CREATE_RESOURCE)
    def fetch_signing_files(self,
                            bundle_id_identifier: str,
                            certificate_key: Optional[Types.CertificateKeyArgument] = None,
                            certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
                            p12_container_password: str = '',
                            platform: BundleIdPlatform = BundleIdPlatform.IOS,
                            profile_type: ProfileType = ProfileType.IOS_APP_DEVELOPMENT,
                            bundle_id_identifier_strict_match: bool = False,
                            create_resource: bool = False) -> Tuple[List[Profile], List[SigningCertificate]]:
        """
        Fetch provisioning profiles and code signing certificates
        for Bundle ID with given identifier
        """

        private_key = _get_certificate_key(certificate_key, certificate_key_password)
        if private_key is None:
            raise AppStoreConnectError(f'Cannot save {SigningCertificate.s} without certificate private key')

        bundle_ids = self._get_or_create_bundle_ids(
            bundle_id_identifier,
            platform,
            create_resource,
            bundle_id_identifier_strict_match,
        )
        certificates = self._get_or_create_certificates(
            profile_type, certificate_key, certificate_key_password, create_resource)
        profiles = self._get_or_create_profiles(bundle_ids, certificates, profile_type, create_resource, platform)

        self._save_certificates(certificates, private_key, p12_container_password)
        self._save_profiles(profiles)
        return profiles, certificates

    def _get_or_create_bundle_ids(self,
                                  bundle_id_identifier: str,
                                  platform: BundleIdPlatform,
                                  create_resource: bool,
                                  strict_match: bool) -> List[BundleId]:
        bundle_ids = self.list_bundle_ids(
            bundle_id_identifier,
            platform=platform,
            bundle_id_identifier_strict_match=strict_match,
            should_print=False,
        )
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
                                 profile_type: ProfileType,
                                 platform: Optional[BundleIdPlatform] = None) -> Iterator[Profile]:
        if not bundle_ids_without_profiles:
            return []
        if platform is None:
            platform = bundle_ids_without_profiles[0].attributes.platform

        devices = self.list_devices(platform=platform, device_status=DeviceStatus.ENABLED, should_print=False)
        for bundle_id in bundle_ids_without_profiles:
            yield self.create_profile(
                bundle_id.id,
                [certificate.id for certificate in certificates],
                [device.id for device in devices],
                profile_type=profile_type,
                should_print=False,
            )

    def _get_or_create_profiles(self,
                                bundle_ids: Sequence[BundleId],
                                certificates: Sequence[SigningCertificate],
                                profile_type: ProfileType,
                                create_resource: bool,
                                platform: Optional[BundleIdPlatform] = None):
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
            missing = ', '.join(f'"{bid.attributes.identifier}" [{bid.id}]' for bid in bundle_ids_without_profiles)
            raise AppStoreConnectError(f'Did not find {profile_type} {Profile.s} for {BundleId.s}: {missing}')

        created_profiles = self._create_missing_profiles(
            bundle_ids_without_profiles, certificates, profile_type, platform)
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
        profile_path = self._get_unique_path(
            f'{profile.get_display_info()}{profile.profile_extension}', self.profiles_directory)
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
                export_path=certificate_path)
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
