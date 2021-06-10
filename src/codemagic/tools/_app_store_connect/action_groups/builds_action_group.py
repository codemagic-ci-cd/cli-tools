from __future__ import annotations

from abc import ABCMeta

from codemagic import cli
from codemagic.apple.resources import Build
from codemagic.apple.resources import PreReleaseVersion
from codemagic.apple.resources import ResourceId

from ..abstract_base_action import AbstractBaseAction
from ..action_group import AppStoreConnectActionGroup
from ..arguments import BuildArgument


class BuildsActionGroup(AbstractBaseAction, metaclass=ABCMeta):

    @cli.action('get',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BUILDS)
    def get_build(self, build_id: ResourceId, should_print: bool = True) -> Build:
        """
        Get information about a specific build
        """

        return self._get_resource(build_id, self.api_client.builds, should_print)

    @cli.action('pre-release-version',
                BuildArgument.BUILD_ID_RESOURCE_ID,
                action_group=AppStoreConnectActionGroup.BUILDS)
    def get_build_pre_release_version(self, build_id: ResourceId, should_print: bool = True) -> PreReleaseVersion:
        """
        Get the prerelease version for a specific build
        """

        return self._get_related_resource(
            build_id,
            Build,
            PreReleaseVersion,
            self.api_client.builds.read_pre_release_version,
            should_print,
        )
