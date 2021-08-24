from typing import List
from typing import Sequence
from typing import Set
from typing import Tuple

from codemagic import cli
from codemagic.apple import AppStoreConnectApiError
from codemagic.apple.resources import BetaGroup
from codemagic.apple.resources import ResourceId
from codemagic.cli import Colors

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument
from ..errors import AppStoreConnectError


class BetaGroupsActionGroup(AbstractBaseAction):

    @cli.action('add-build',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.BETA_GROUP_NAMES_REQUIRED,
                action_group=AppStoreConnectActionGroup.BETA_GROUPS)
    def add_build_to_beta_groups(self, build_id: ResourceId, beta_group_names: Sequence[str]):
        """
        Add build to Beta groups
        """
        self.logger.info(
            Colors.BLUE(f"Adding build '{build_id}' to the following beta groups: {', '.join(beta_group_names)}."))

        matched_beta_groups, matched_beta_group_names = self._get_beta_groups(build_id, beta_group_names)

        errors = []
        for beta_group in matched_beta_groups:
            beta_group_name = beta_group.attributes.name
            try:
                self.api_client.beta_groups.add_build(beta_group, build_id)
            except AppStoreConnectApiError as e:
                errors.append((beta_group_name, e.error_response))
            else:
                self.logger.info(Colors.GREEN(f"Added build '{build_id}' to '{beta_group_name}' beta group"))

        missing_beta_group_names = set(beta_group_names) - matched_beta_group_names
        if missing_beta_group_names:
            self.logger.warning(Colors.YELLOW(
                '\n'.join(f"Cannot find Beta group with the name '{name}'" for name in missing_beta_group_names)))

        if errors:
            error_lines = [
                f"Failed to add a build '{build_id}' to '{group_name}' beta group. {error_response}"
                for group_name, error_response in errors
            ]
            raise AppStoreConnectError('\n'.join(error_lines))

    @cli.action('remove-build',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                BuildArgument.BETA_GROUP_NAMES_REQUIRED,
                action_group=AppStoreConnectActionGroup.BETA_GROUPS)
    def remove_build_from_beta_groups(self, build_id: ResourceId, beta_group_names: Sequence[str]):
        """
        Remove build from Beta groups
        """
        self.logger.info(
            Colors.BLUE(f"Removing build '{build_id}' from the following beta groups: {', '.join(beta_group_names)}."))

        matched_beta_groups, matched_beta_group_names = self._get_beta_groups(build_id, beta_group_names)

        errors = []
        for beta_group in matched_beta_groups:
            beta_group_name = beta_group.attributes.name
            try:
                self.api_client.beta_groups.remove_build(beta_group, build_id)
            except AppStoreConnectApiError as e:
                errors.append((beta_group_name, e.error_response))
            else:
                self.logger.info(Colors.GREEN(f"Removed build '{build_id}' from '{beta_group_name}' beta group"))

        missing_beta_group_names = set(beta_group_names) - matched_beta_group_names
        if missing_beta_group_names:
            self.logger.warning(Colors.YELLOW(
                '\n'.join(f"Cannot find Beta group with the name '{name}'" for name in missing_beta_group_names)))

        if errors:
            error_lines = [
                f"Failed to remove a build '{build_id}' from '{group_name}' beta group. {error_response}"
                for group_name, error_response in errors
            ]
            raise AppStoreConnectError('\n'.join(error_lines))

    def _get_beta_groups(
            self,
            build_id: ResourceId,
            beta_group_names: Sequence[str]) -> Tuple[List[BetaGroup], Set[str]]:

        try:
            app = self.api_client.builds.read_app(build_id)
        except AppStoreConnectApiError as e:
            raise AppStoreConnectError(str(e))

        resource_filter = self.api_client.beta_groups.Filter(app=app.id)
        app_beta_groups = self.api_client.beta_groups.list(resource_filter=resource_filter)

        matched_beta_groups = [
            beta_group for beta_group in app_beta_groups if beta_group.attributes.name in beta_group_names]

        matched_beta_group_names = set(beta_group.attributes.name for beta_group in app_beta_groups)

        return matched_beta_groups, matched_beta_group_names
