from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast

from codemagic import cli
from codemagic.apple.resources import BundleIdPlatform
from codemagic.apple.resources import Device
from codemagic.apple.resources import DeviceStatus
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BundleIdArgument
from ..arguments import DeviceArgument
from ..arguments import Types
from ..errors import AppStoreConnectError

if TYPE_CHECKING:
    from codemagic.apple.app_store_connect.resource_manager import CreatingResourceManager
    from codemagic.apple.app_store_connect.resource_manager import ListingResourceManager


class DevicesActionGroup(AbstractBaseAction, metaclass=ABCMeta):
    @cli.action(
        "list",
        BundleIdArgument.PLATFORM_OPTIONAL,
        DeviceArgument.DEVICE_NAME_OPTIONAL,
        DeviceArgument.DEVICE_STATUS,
        action_group=AppStoreConnectActionGroup.DEVICES,
        deprecation_info=cli.ActionDeprecationInfo("list-devices", "0.49.0"),
    )
    def list_devices(
        self,
        platform: Optional[BundleIdPlatform] = None,
        device_name: Optional[str] = None,
        device_status: Optional[DeviceStatus] = None,
        should_print: bool = True,
    ) -> List[Device]:
        """
        List Devices from Apple Developer portal matching given constraints
        """

        device_filter = self.api_client.devices.Filter(
            name=device_name,
            platform=platform,
            status=device_status,
        )
        return self._list_resources(
            device_filter,
            cast("ListingResourceManager[Device]", self.api_client.devices),
            should_print,
        )

    @cli.action(
        "register",
        BundleIdArgument.PLATFORM,
        DeviceArgument.DEVICE_NAME,
        DeviceArgument.DEVICE_UDIDS,
        DeviceArgument.IGNORE_REGISTRATION_ERRORS,
        action_group=AppStoreConnectActionGroup.DEVICES,
        deprecation_info=cli.ActionDeprecationInfo("register-device", "0.49.0"),
    )
    def register_device(
        self,
        platform: BundleIdPlatform,
        device_name: str,
        device_udid: Optional[str] = None,  # Deprecated in https://github.com/codemagic-ci-cd/cli-tools/pull/331
        device_udids: Optional[
            Union[
                str,
                Types.DeviceUdidsArgument,
                Sequence[Union[str, Types.DeviceUdidsArgument]],
            ]
        ] = None,
        ignore_registration_errors: bool = DeviceArgument.IGNORE_REGISTRATION_ERRORS.get_default(),
        should_print: bool = True,
    ) -> List[Device]:
        """
        Register new Devices for app development
        """
        if not device_udids and not device_udid:
            DeviceArgument.DEVICE_UDIDS.raise_argument_error("At least one device UDID is required")

        if device_udids is None:
            device_udids = []
        if isinstance(device_udids, str) or isinstance(device_udids, Types.DeviceUdidsArgument):
            device_udids = [device_udids]

        if device_udid:
            device_udids = [device_udid, *device_udids]

        device_udids_values: List[str] = []
        for device_udids in device_udids:
            if isinstance(device_udids, Types.DeviceUdidsArgument):
                device_udids_values.extend(device_udids.value)
            else:
                device_udids_values.append(device_udids)

        registered_devices = []
        for device_udid in device_udids_values:
            try:
                device = self._create_resource(
                    cast("CreatingResourceManager[Device]", self.api_client.devices),
                    should_print,
                    udid=device_udid,
                    name=device_name,
                    platform=platform,
                )
            except AppStoreConnectError as error:
                if not ignore_registration_errors:
                    raise error
                self.logger.error(Colors.YELLOW(f"Failed to register a device: {error.args[0]}"))
            else:
                registered_devices.append(device)

            self.echo("") if should_print else None

        return registered_devices
