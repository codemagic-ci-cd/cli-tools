#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
from functools import lru_cache
from typing import Optional

import jwt

from codemagic import cli
from codemagic.apple.app_store_connect import AppStoreConnectApiClient
from codemagic.apple.app_store_connect import IssuerId
from codemagic.apple.app_store_connect import KeyIdentifier
from codemagic.mixins import PathFinderMixin
from codemagic.models import Certificate
from codemagic.models import ProvisioningProfile
from codemagic.utilities import log

from . import action_groups
from . import actions
from . import mixins
from .arguments import AppStoreConnectArgument
from .arguments import Types
from .resource_printer import ResourcePrinter


@cli.common_arguments(*AppStoreConnectArgument)
class AppStoreConnect(
    cli.CliApp,
    action_groups.AppStoreVersionLocalizationsActionGroup,
    action_groups.AppStoreVersionPhasedReleasesActionGroup,
    action_groups.AppStoreVersionSubmissionsActionGroup,
    action_groups.AppStoreVersionsActionGroup,
    action_groups.AppsActionGroup,
    action_groups.BetaAppReviewSubmissionsActionGroup,
    action_groups.BetaBuildLocalizationsActionGroup,
    action_groups.BetaGroupsActionGroup,
    action_groups.BuildsActionGroup,
    action_groups.BundleIdsActionGroup,
    action_groups.CertificatesActionGroup,
    action_groups.DevicesActionGroup,
    action_groups.ProfilesActionGroup,
    action_groups.ReviewSubmissionItemsActionGroup,
    action_groups.ReviewSubmissionsActionGroup,
    actions.FetchSigningFilesAction,
    actions.GetLatestAppStoreBuildNumberAction,
    actions.GetLatestBuildNumberAction,
    actions.GetLatestTestflightBuildNumberAction,
    actions.PublishAction,
    actions.SubmitToAppStoreAction,
    actions.SubmitToTestFlightAction,
    mixins.ResourceManagerMixin,
    mixins.SigningFileSaverMixin,
    PathFinderMixin,
):
    """
    Interact with Apple services via App Store Connect API
    """

    def __init__(
        self,
        key_identifier: Optional[KeyIdentifier],
        issuer_id: Optional[IssuerId],
        private_key: Optional[str],
        log_requests: bool = False,
        unauthorized_request_retries: int = 1,
        server_error_retries: int = 1,
        enable_jwt_cache: bool = False,
        json_output: bool = False,
        profiles_directory: pathlib.Path = ProvisioningProfile.DEFAULT_LOCATION,
        certificates_directory: pathlib.Path = Certificate.DEFAULT_LOCATION,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.profiles_directory = profiles_directory
        self.certificates_directory = certificates_directory
        self.printer = ResourcePrinter(bool(json_output), self.echo)
        self._key_identifier = key_identifier
        self._issuer_id = issuer_id
        self._private_key = private_key
        self._log_requests = log_requests
        self._unauthorized_request_retries = unauthorized_request_retries
        self._server_error_retries = server_error_retries
        self._enable_jwt_cache = enable_jwt_cache

    @classmethod
    def from_cli_args(cls, cli_args: argparse.Namespace) -> AppStoreConnect:
        key_identifier_argument = AppStoreConnectArgument.KEY_IDENTIFIER.from_args(cli_args)
        issuer_id_argument = AppStoreConnectArgument.ISSUER_ID.from_args(cli_args)
        private_key_argument = AppStoreConnectArgument.PRIVATE_KEY.from_args(cli_args)
        unauthorized_request_retries = Types.ApiUnauthorizedRetries.resolve_value(cli_args.unauthorized_request_retries)
        server_error_retries = Types.ApiServerErrorRetries.resolve_value(cli_args.server_error_retries)
        disable_jwt_cache = AppStoreConnectArgument.DISABLE_JWT_CACHE.from_args(cli_args)

        app_store_connect = AppStoreConnect(
            key_identifier=key_identifier_argument.value if key_identifier_argument else None,
            issuer_id=issuer_id_argument.value if issuer_id_argument else None,
            private_key=private_key_argument.value if private_key_argument else None,
            log_requests=cli_args.log_requests,
            unauthorized_request_retries=unauthorized_request_retries,
            server_error_retries=server_error_retries,
            enable_jwt_cache=not disable_jwt_cache,
            json_output=cli_args.json_output,
            profiles_directory=cli_args.profiles_directory,
            certificates_directory=cli_args.certificates_directory,
            **cls._parent_class_kwargs(cli_args),
        )

        cli_action = app_store_connect._get_invoked_cli_action(cli_args)
        if cli_action.action_options.get("requires_api_client", True):
            app_store_connect._assert_api_client_credentials()

        return app_store_connect

    def _assert_api_client_credentials(self, custom_error: Optional[str] = None):
        if self._issuer_id is None:
            if custom_error:
                default_message = AppStoreConnectArgument.ISSUER_ID.get_missing_value_error_message()
                raise AppStoreConnectArgument.ISSUER_ID.raise_argument_error(f"{default_message}. {custom_error}")
            else:
                raise AppStoreConnectArgument.ISSUER_ID.raise_argument_error()

        if self._key_identifier is None:
            if custom_error:
                default_message = AppStoreConnectArgument.KEY_IDENTIFIER.get_missing_value_error_message()
                raise AppStoreConnectArgument.KEY_IDENTIFIER.raise_argument_error(f"{default_message}. {custom_error}")
            else:
                raise AppStoreConnectArgument.KEY_IDENTIFIER.raise_argument_error()

        try:
            self._resolve_app_store_connect_private_key()
        except ValueError as ve:
            custom_error = ve.args[0] if ve.args else custom_error
            if custom_error:
                default_message = AppStoreConnectArgument.PRIVATE_KEY.get_missing_value_error_message()
                AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error(f"{default_message}. {custom_error}")
            else:
                AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error()

    def _resolve_app_store_connect_private_key(self):
        if self._private_key is not None:
            return

        for keys_path in Types.PrivateKeyArgument.PRIVATE_KEY_LOCATIONS:
            try:
                api_key = next(keys_path.expanduser().glob(f"AuthKey_{self._key_identifier}.p8"))
            except StopIteration:
                continue

            try:
                private_key_argument = Types.PrivateKeyArgument(api_key.read_text())
            except ValueError:
                raise ValueError(f"Provided value in {api_key} is not valid")
            self._private_key = private_key_argument.value
            break
        else:
            raise ValueError()

    def _validate_api_client_key(self, client: AppStoreConnectApiClient):
        """
        When running from a CLI context, ensure that App Store Connect API client is using valid
        private key for JWT generation. In case of invalid key exit with descriptive argument error.
        """

        if not self.is_cli_invocation():
            return

        try:
            client.generate_auth_headers()
        except jwt.InvalidKeyError:
            log.get_file_logger(self.__class__).exception("Invalid App Store Connect API key")
            asc_docs_base_url = "https://developer.apple.com/documentation/appstoreconnectapi"
            error_message = (
                "Invalid App Store Connect API key. Make sure to use the private API key downloaded from "
                "App Store Connect. Read more about creating App Store Connect API keys from "
                f"{asc_docs_base_url}/creating_api_keys_for_app_store_connect_api"
            )
            AppStoreConnectArgument.PRIVATE_KEY.raise_argument_error(error_message)

    @lru_cache(1)
    def _get_api_client(self) -> AppStoreConnectApiClient:
        assert self._key_identifier is not None
        assert self._issuer_id is not None
        assert self._private_key is not None
        client = AppStoreConnectApiClient(
            self._key_identifier,
            self._issuer_id,
            self._private_key,
            log_requests=self._log_requests,
            unauthorized_request_retries=self._unauthorized_request_retries,
            server_error_retries=self._server_error_retries,
            enable_jwt_cache=self._enable_jwt_cache,
        )
        self._validate_api_client_key(client)
        return client

    @property
    def api_client(self) -> AppStoreConnectApiClient:
        return self._get_api_client()


if __name__ == "__main__":
    AppStoreConnect.invoke_cli()
