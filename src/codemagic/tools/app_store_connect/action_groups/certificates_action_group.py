from __future__ import annotations

import pathlib
from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple.resources import CertificateType
from codemagic.apple.resources import ProfileType
from codemagic.apple.resources import ResourceId
from codemagic.apple.resources import SigningCertificate
from codemagic.cli import Colors
from codemagic.models import Certificate
from codemagic.models import PrivateKey

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import CertificateArgument
from ..arguments import CommonArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager


class CertificatesActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "create",
        CertificateArgument.CERTIFICATE_TYPE,
        CertificateArgument.PRIVATE_KEY,
        CertificateArgument.PRIVATE_KEY_PASSWORD,
        CertificateArgument.P12_CONTAINER_PASSWORD,
        CertificateArgument.P12_CONTAINER_SAVE_PATH,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.CERTIFICATES,
        deprecation_info=cli.ActionDeprecationInfo("create-certificate", "0.49.0"),
    )
    def create_certificate(
        self,
        certificate_type: CertificateType = CertificateType.IOS_DEVELOPMENT,
        certificate_key: Optional[Union[PrivateKey, Types.CertificateKeyArgument]] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
        p12_container_password: str = "",
        p12_container_save_path: Optional[pathlib.Path] = None,
        save: bool = False,
        should_print: bool = True,
    ) -> SigningCertificate:
        """
        Create code signing certificates of given type
        """

        private_key = self._get_certificate_key(certificate_key, certificate_key_password)
        if private_key is None:
            raise AppStoreConnectError("Cannot create resource without certificate private key")

        csr = Certificate.create_certificate_signing_request(private_key)
        csr_content = Certificate.get_certificate_signing_request_content(csr)

        create_params = dict(csr_content=csr_content, certificate_type=certificate_type, omit_keys=["csr_content"])
        certificate = self._create_resource(
            cast("CreatingResourceManager[SigningCertificate]", self.api_client.signing_certificates),
            should_print,
            **create_params,
        )

        if save:
            self._save_certificate(certificate, private_key, p12_container_password, p12_container_save_path)
        return certificate

    @cli.action(
        "get",
        CertificateArgument.CERTIFICATE_RESOURCE_ID,
        CertificateArgument.PRIVATE_KEY,
        CertificateArgument.PRIVATE_KEY_PASSWORD,
        CertificateArgument.P12_CONTAINER_PASSWORD,
        CertificateArgument.P12_CONTAINER_SAVE_PATH,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.CERTIFICATES,
        deprecation_info=cli.ActionDeprecationInfo("get-certificate", "0.49.0"),
    )
    def get_certificate(
        self,
        certificate_resource_id: ResourceId,
        certificate_key: Optional[Union[PrivateKey, Types.CertificateKeyArgument]] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
        p12_container_password: str = "",
        p12_container_save_path: Optional[pathlib.Path] = None,
        save: bool = False,
        should_print: bool = True,
    ) -> SigningCertificate:
        """
        Get specified Signing Certificate from Apple Developer portal
        """

        private_key = self._get_certificate_key(certificate_key, certificate_key_password)
        if save and not private_key:
            raise AppStoreConnectError("Cannot save resource without certificate private key")

        certificate = self._get_resource(certificate_resource_id, self.api_client.signing_certificates, should_print)

        if save:
            self._save_certificate(
                certificate,
                cast(PrivateKey, private_key),
                p12_container_password,
                p12_container_save_path,
            )
        return certificate

    @cli.action(
        "delete",
        CertificateArgument.CERTIFICATE_RESOURCE_ID,
        CommonArgument.IGNORE_NOT_FOUND,
        action_group=AppStoreConnectActionGroup.CERTIFICATES,
        deprecation_info=cli.ActionDeprecationInfo("delete-certificate", "0.49.0"),
    )
    def delete_certificate(
        self,
        certificate_resource_id: ResourceId,
        ignore_not_found: bool = False,
    ) -> None:
        """
        Delete specified Signing Certificate from Apple Developer portal
        """

        self._delete_resource(self.api_client.signing_certificates, certificate_resource_id, ignore_not_found)

    @cli.action(
        "list",
        CertificateArgument.CERTIFICATE_TYPES_OPTIONAL,
        CertificateArgument.PROFILE_TYPE_OPTIONAL,
        CertificateArgument.DISPLAY_NAME,
        CertificateArgument.PRIVATE_KEY,
        CertificateArgument.PRIVATE_KEY_PASSWORD,
        CertificateArgument.P12_CONTAINER_PASSWORD,
        CommonArgument.SAVE,
        action_group=AppStoreConnectActionGroup.CERTIFICATES,
        deprecation_info=cli.ActionDeprecationInfo("list-certificates", "0.49.0"),
    )
    def list_certificates(
        self,
        certificate_types: Optional[Union[CertificateType, Sequence[CertificateType]]] = None,
        profile_type: Optional[ProfileType] = None,
        display_name: Optional[str] = None,
        certificate_key: Optional[Union[PrivateKey, Types.CertificateKeyArgument]] = None,
        certificate_key_password: Optional[Types.CertificateKeyPasswordArgument] = None,
        p12_container_password: str = "",
        save: bool = False,
        should_print: bool = True,
        **_deprecated_kwargs,
    ) -> List[SigningCertificate]:
        """
        List Signing Certificates from Apple Developer Portal matching given constraints
        """

        private_key = self._get_certificate_key(certificate_key, certificate_key_password)
        if save and private_key is None:
            raise AppStoreConnectError("Cannot create or save resource without certificate private key")

        _certificate_type: Optional[CertificateType] = _deprecated_kwargs.get("certificate_type")
        if isinstance(_certificate_type, CertificateType):
            warning = (
                "Deprecation warning! Keyword argument "
                '"certificate_type: Optional[CertificateType]" is deprecated in favor of '
                '"certificate_types: Optional[Union[CertificateType, Sequence[CertificateType]]]", '
                "and is subject for removal."
            )
            self.logger.warning(Colors.RED(warning))
            certificate_types = _certificate_type

        certificate_types_filter = CertificateType.resolve_applicable_types(
            certificate_types=certificate_types,
            profile_type=profile_type,
        )

        certificate_filter = self.api_client.signing_certificates.Filter(
            certificate_type=certificate_types_filter if certificate_types_filter else None,
            display_name=display_name,
        )
        certificates = self._list_resources(
            certificate_filter,
            cast("ListingResourceManager[SigningCertificate]", self.api_client.signing_certificates),
            should_print,
        )

        if private_key:
            certificates = [
                certificate
                for certificate in certificates
                if Certificate.from_ans1(certificate.asn1_content).is_signed_with(private_key)
            ]
            self.printer.log_filtered(SigningCertificate, certificates, "for given private key")
            for certificate in certificates:
                self.logger.info(f"- {certificate.get_display_info()}")

        if save:
            self._save_certificates(
                certificates,
                cast(PrivateKey, private_key),
                p12_container_password,
            )

        return certificates
