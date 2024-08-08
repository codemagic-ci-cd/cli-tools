from abc import ABC
from typing import List

from codemagic import cli
from codemagic.cli import Colors
from codemagic.google.errors import GoogleError
from codemagic.google.resources import OrderBy
from codemagic.google.resources import Release
from codemagic.google.resources.identifiers import AppIdentifier

from ..arguments import FirebaseArgument
from ..arguments import ReleasesArgument
from ..arguments import ResourcesArgument
from ..errors import FirebaseAppDistributionError
from ..firebase_app_distribution_action import FirebaseAppDistributionAction
from ..resource_printer import ResourcePrinter
from .firebase_action_groups import FirebaseActionGroups


class ReleasesActionGroup(FirebaseAppDistributionAction, ABC):
    @cli.action(
        "list",
        ReleasesArgument.APP_ID,
        ResourcesArgument.LIMIT,
        ResourcesArgument.ORDER_BY,
        FirebaseArgument.JSON_OUTPUT,
        action_group=FirebaseActionGroups.RELEASES,
    )
    def list_releases(
        self,
        app_id: str,
        limit: int = ResourcesArgument.LIMIT.get_default(),
        order_by: OrderBy = ResourcesArgument.ORDER_BY.get_default(),
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        """
        List releases for the Firebase application
        """

        app_identifier = AppIdentifier(self.project_number, app_id)
        try:
            releases = self.client.releases.list(app_identifier, order_by, limit)
        except GoogleError as e:
            raise FirebaseAppDistributionError(str(e))

        if not releases:
            self.logger.info(Colors.YELLOW(f"No releases available for {app_identifier.app_id}"))
        else:
            printer = ResourcePrinter(json_output, self.echo)
            printer.print_resources(releases, should_print)

        return releases
