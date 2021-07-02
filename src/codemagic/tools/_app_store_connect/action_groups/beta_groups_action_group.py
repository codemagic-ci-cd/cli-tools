from typing import Sequence
from typing import Union

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.app_store_connect.builds import Builds
from codemagic.apple.app_store_connect.provisioning.beta_groups import BetaGroups
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument
from ..errors import AppStoreConnectError


class BetaGroupsActionGroup(AbstractBaseAction):

    @cli.action('add-build',
                BuildArgument.BUILD_ID_RESOURCE_ID_REQUIRED,
                BuildArgument.BETA_GROUP_NAMES_REQUIRED,
                action_group=AppStoreConnectActionGroup.BETA_GROUPS)
    def add_build(self, build_id: Union[ResourceId, Build], beta_group_names: Sequence[str]):
        """
        Add build to a Beta group
        """
        builds_manager = Builds(client=self.api_client)
        app = builds_manager.read_app(build_id)

        beta_groups = []

        beta_groups_manager = BetaGroups(client=self.api_client)
        for name in beta_group_names:
            resource_filter = beta_groups_manager.Filter(app=app.id, name=name)
            matched_beta_groups = beta_groups_manager.list(resource_filter=resource_filter)
            if not matched_beta_groups:
                self.logger.info(Colors.YELLOW(f"Cannot find Beta group with the name '{name}'"))
                continue
            beta_groups.extend(matched_beta_groups)

        errors = []
        for beta_group in beta_groups:
            try:
                beta_groups_manager.add_build(beta_group, build_id)
                self.logger.error(Colors.GREEN(f"Added build '{build_id}' to '{beta_group.attributes.name}'"))
            except AppStoreConnectApiError as e:
                errors.append([beta_group.attributes.name, e.error_response])

        if errors:
            message = f"Failed to add a build '{build_id}' to '{{name}}'. {{error_response}}"
            raise AppStoreConnectError(
                '\n'.join(
                    message.format(name=name, error_response=error_response) for name, error_response in errors
                )
            )

    @cli.action('remove-build',
                BuildArgument.BUILD_ID_RESOURCE_ID_REQUIRED,
                BuildArgument.BETA_GROUP_NAMES_REQUIRED,
                action_group=AppStoreConnectActionGroup.BETA_GROUPS)
    def remove_build(self, build_id: Union[ResourceId, Build], beta_group_names: Sequence[str]):
        """
        Remove build from a Beta group
        """
        builds_manager = Builds(client=self.api_client)
        app = builds_manager.read_app(build_id)

        beta_groups = []

        beta_groups_manager = BetaGroups(client=self.api_client)
        for name in beta_group_names:
            resource_filter = beta_groups_manager.Filter(app=app.id, name=name)
            matched_beta_groups = beta_groups_manager.list(resource_filter=resource_filter)
            if not matched_beta_groups:
                self.logger.info(Colors.YELLOW(f"Cannot find Beta group with the name '{name}'"))
                continue
            beta_groups.extend(matched_beta_groups)

        for beta_group in beta_groups:
            beta_groups_manager.remove_build(beta_group, build_id)
            self.logger.info(Colors.GREEN(f"Removed build '{build_id}' from '{beta_group.attributes.name}'"))
