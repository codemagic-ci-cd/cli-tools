#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import tempfile
import time
from functools import lru_cache
from typing import Callable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.apple.resources import App
from codemagic.apple.resources import AppStoreState
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
from codemagic.apple.resources import Resource
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Argument
from codemagic.cli import Colors
from codemagic.mixins import PathFinderMixin
from codemagic.models import Altool
from codemagic.models import Certificate
from codemagic.models import PrivateKey
from codemagic.models import ProvisioningProfile
from codemagic.models.application_package import Ipa
from codemagic.models.application_package import MacOsPackage

from ._app_store_connect.action_group import AppStoreConnectActionGroup
from ._app_store_connect.arguments import AppArgument
from ._app_store_connect.arguments import AppStoreArgument
from ._app_store_connect.arguments import AppStoreConnectArgument
from ._app_store_connect.arguments import AppStoreVersionArgument
from ._app_store_connect.arguments import BuildArgument
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
            return PrivateKey.from_buffer(certificate_key.value, password)
        except ValueError:
            CertificateArgument.PRIVATE_KEY.raise_argument_error('Not a valid certificate private key')
    return None


@cli.common_arguments(*AppStoreConnectArgument)
class AppStoreConnect(cli.CliApp, PathFinderMixin):
    """
    Utility to download code signing certificates and provisioning profiles
    from Apple Developer Portal using App Store Connect API to perform iOS code signing
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
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._log_api_requests = log_requests

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

        app_store_connect = AppStoreConnect(
            key_identifier=key_identifier_argument.value,
            issuer_id=issuer_id_argument.value,
            private_key=private_key_argument.value,
            log_requests=cli_args.log_requests,
            json_output=cli_args.json_output,
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            **cls._parent_class_kwargs(cli_args),
        )
        # Validate that App Store Connect credentials are fine
        _ = app_store_connect.api_client
        return app_store_connect

    @lru_cache(1)
    def _get_api_client(self) -> AppStoreConnectApiClient:
        return AppStoreConnectApiClient(
            self._key_identifier,
            self._issuer_id,
            self._private_key,
            log_requests=self._log_api_requests,
        )

    @property
    def api_client(self) -> AppStoreConnectApiClient:
        return self._get_api_client()

    @lru_cache(1)
    def _get_altool(self) -> Altool:
        try:
            return Altool(
                key_identifier=self._key_identifier,
                issuer_id=self._issuer_id,
                private_key=self._private_key,
            )
        except ValueError as ve:
            raise AppStoreConnectError(str(ve))

    @property
    def altool(self) -> Altool:
        return self._get_altool()

    def _create_resource(self, resource_manager, should_print, **create_params):
        omit_keys = create_params.pop('omit_keys', tuple())
        self.printer.log_creating(
            resource_manager.resource_type,
            **{k: v for k, v in create_params.items() if k not in omit_keys},
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

    def _list_resources(self,
                        resource_filter,
                        resource_manager,
                        should_print: bool,
                        filter_predicate: Optional[Callable[[Resource], bool]] = None):
        try:
            resources = resource_manager.list(resource_filter=resource_filter)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        if filter_predicate is not None:
            resources = list(filter(filter_predicate, resources))

        self.printer.log_found(resource_manager.resource_type, resources, resource_filter)
        self.printer.print_resources(resources, should_print)
        return resources

    def _list_related_resources(self,
                                resource_id: ResourceId,
                                resource_type,
                                related_resource_type,
                                list_related_resources_method,
                                resource_filter,
                                should_print: bool):
        self.printer.log_get_related(related_resource_type, resource_type, resource_id)
        try:
            kwargs = {'resource_filter': resource_filter} if resource_filter else {}
            resources = list_related_resources_method(resource_id, **kwargs)
        except AppStoreConnectApiError as api_error:
            raise AppStoreConnectError(str(api_error))

        self.printer.log_found(related_resource_type, resources, resource_filter, resource_type)
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

    @cli.action('list',
                BundleIdArgument.BUNDLE_ID_IDENTIFIER_OPTIONAL,
                AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
                AppArgument.APPLICATION_NAME,
                AppArgument.APPLICATION_SKU,
                AppStoreVersionArgument.APP_STORE_VERSION,
                AppStoreVersionArgument.PLATFORM,
                AppStoreVersionArgument.VERSION_STATE,
                action_group=AppStoreConnectActionGroup.APPS)
    def list_apps(self,
                  bundle_id_identifier: Optional[str] = None,
                  application_id: Optional[ResourceId] = None,
                  application_name: Optional[str] = None,
                  application_sku: Optional[str] = None,
                  app_store_version: Optional[str] = None,
                  app_store_version_platform: Optional[Platform] = None,
                  app_store_version_app_store_state: Optional[AppStoreState] = None,
                  should_print: bool = True) -> List[App]:
        """
        Find and list apps added in App Store Connect
        """

        apps_filter = self.api_client.apps.Filter(
            bundle_id=bundle_id_identifier,
            id=application_id,
            name=application_name,
            sku=application_sku,
            app_store_versions=app_store_version,
            app_store_versions_platform=app_store_version_platform,
            app_store_versions_app_store_state=app_store_version_app_store_state,
        )
        return self._list_resources(apps_filter, self.api_client.apps, should_print)

    @cli.action('get', AppArgument.APPLICATION_ID_RESOURCE_ID, action_group=AppStoreConnectActionGroup.APPS)
    def get_app(self, application_id: ResourceId, should_print: bool = True) -> App:
        """
        Get information about a specific app
        """

        return self._get_resource(application_id, self.api_client.apps, should_print)

    @cli.action('builds', AppArgument.APPLICATION_ID_RESOURCE_ID, action_group=AppStoreConnectActionGroup.APPS)
    def list_app_builds(self, application_id: ResourceId, should_print: bool = True) -> List[Build]:
        """
        Get a list of builds associated with a specific app
        """

        return self._list_related_resources(
            application_id, App, Build, self.api_client.apps.list_builds, None, should_print)

    @cli.action('list-builds',
                AppArgument.APPLICATION_ID_RESOURCE_ID_OPTIONAL,
                BuildArgument.EXPIRED,
                BuildArgument.NOT_EXPIRED,
                BuildArgument.BUILD_ID_RESOURCE_ID,
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
    def _get_latest_build_number(cls, builds: List[Build]) -> Optional[int]:
        try:
            latest_build_number = max(int(build.attributes.version) for build in builds)
        except ValueError:
            return None
        cls.echo(str(latest_build_number))
        return latest_build_number

    @cli.action('get-latest-app-store-build-number',
                AppArgument.APPLICATION_ID_RESOURCE_ID,
                AppStoreVersionArgument.APP_STORE_VERSION,
                CommonArgument.PLATFORM)
    def get_latest_app_store_build_number(self,
                                          application_id: ResourceId,
                                          app_store_version: Optional[str] = None,
                                          platform: Optional[Platform] = None,
                                          should_print: bool = False) -> Optional[int]:
        """
        Get latest App Store build number for the given application
        """
        versions_client = self.api_client.app_store_versions
        versions_filter = versions_client.Filter(version_string=app_store_version, platform=platform)
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
                                           should_print: bool = False) -> Optional[int]:
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
                DeviceArgument.DEVICE_NAME,
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
        Get specified Signing Certificate from Apple Developer portal
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
            raise AppStoreConnectError('Cannot create or save resource without private key')

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

    @cli.action('publish',
                AppStoreArgument.ARTIFACT_PATTERNS,
                action_group=AppStoreConnectActionGroup.APP_STORE)
    def publish(self, artifact_patterns: Sequence[pathlib.Path]) -> None:
        """
        Publish artifacts to App Store
        """

        failed_packages: List[str] = []
        for application_package in self._get_publishing_application_packages(artifact_patterns):
            try:
                self._publish_application_package(application_package)
            except IOError as error:
                # TODO: Should we fail the whole action on first publishing failure?
                failed_packages.append(str(application_package.path))
                self.logger.error(Colors.RED(error.args[0]))

        if failed_packages:
            raise AppStoreConnectError(f'Failed to publish {", ".join(failed_packages)}')

    def _publish_application_package(self, application_package: Union[Ipa, MacOsPackage]):
        self.logger.info(Colors.BLUE('\nPublish "%s" to App Store Connect'), application_package.path)
        self.logger.info(application_package.get_text_summary())

        self._validate_artifact_with_altool(application_package.path)
        self._upload_artifact_with_altool(application_package.path)

        bundle_id = application_package.bundle_identifier
        apps = self.list_apps(bundle_id_identifier=bundle_id)
        if not apps:
            raise IOError(f'Did not find app with bundle identifier "{bundle_id}" from App Store Connect')
        # app = apps[0]
        # builds = self.list_app_builds(app.id)

        # TODO: Find corresponding App and Build from App Store Connect that correspond to this upload.
        # TODO: Once found, submit for Build to TestFlight if need be.

    def _get_publishing_application_packages(
            self, artifact_patterns: Sequence[pathlib.Path]) -> List[Union[Ipa, MacOsPackage]]:
        found_artifacts = list(self.find_paths(*artifact_patterns))
        application_packages: List[Union[Ipa, MacOsPackage]] = []
        for path in found_artifacts:
            if path.suffix == '.ipa':
                application_package: Union[Ipa, MacOsPackage] = Ipa(path)
            elif path.suffix == '.pkg':
                application_package = MacOsPackage(path)
            else:
                raise AppStoreConnectError(f'Unsupported package type for App Store Connect publishing: {path}')

            try:
                application_package.get_summary()
            except FileNotFoundError as fnf:
                message = f'Invalid package for App Store Connect publishing: {fnf.args[0]} not found from {path}'
                self.logger.warning(Colors.YELLOW(message))
            except (ValueError, IOError) as error:
                message = f'Unable to process package {path} for App Store Connect publishing: {error.args[0]}'
                self.logger.warning(Colors.YELLOW(message))
            else:
                application_packages.append(application_package)

        if not application_packages:
            patterns = ', '.join(f'"{pattern}"' for pattern in artifact_patterns)
            raise AppStoreConnectError(f'No application packages found for patterns {patterns}')
        return application_packages

    def _validate_artifact_with_altool(self, artifact_path: pathlib.Path):
        self.logger.info(Colors.BLUE('\nValidate archive at "%s" for App Store'), artifact_path)
        result = self.altool.validate_app(artifact_path)
        message = result.success_message or f'No errors validating archive at "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))

    def _upload_artifact_with_altool(self, artifact_path: pathlib.Path):
        self.logger.info(Colors.BLUE('\nUpload archive at "%s" to App Store'), artifact_path)
        result = self.altool.upload_app(artifact_path)
        message = result.success_message or f'No errors uploading "{artifact_path}".'
        self.logger.info(Colors.GREEN(message))

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
            raise AppStoreConnectError(f'Cannot save {SigningCertificate.s} without private key')

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
