from typing import Sequence
from typing import Union

from codemagic import cli
from codemagic.apple.app_store_connect.builds import Builds
from codemagic.apple.app_store_connect.provisioning.beta_groups import BetaGroups
from codemagic.apple.resources import Build
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument


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

        for beta_group in beta_groups:
            beta_groups_manager.add_build(beta_group, build_id)

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
