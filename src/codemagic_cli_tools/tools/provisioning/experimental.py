# @cli.action('find-bundle-id-profiles',
#             BundleIdArgument.BUNDLE_ID_RESOURCE_IDS,
#             ProfileArgument.PROFILE_TYPE,
#             ProfileArgument.PROFILE_STATE,
#             ProfileArgument.PROFILE_NAME,
#             CommonArgument.CREATE_RESOURCE,
#             CommonArgument.JSON_OUTPUT,
#             CommonArgument.SAVE)
# def find_bundle_id_profiles(self,
#                             bundle_id_resource_ids: Sequence[ResourceId],
#                             profile_type: Optional[ProfileType] = None,
#                             profile_state: Optional[ProfileState] = None,
#                             profile_name: Optional[str] = None,
#                             create_resource: bool = CommonArgument.CREATE_RESOURCE.get_default(),
#                             json_output: bool = CommonArgument.JSON_OUTPUT.get_default(),
#                             save: bool = CommonArgument.SAVE.get_default(),
#                             print_resources: bool = True) -> List[Profile]:
#     """
#     Find provisioning profiles from Apple Developer Portal for specified Bundle IDs.
#     """
#     profiles_filter = self.api_client.profiles.Filter(
#         profile_type=profile_type,  profile_state=profile_state, name=profile_name)
#
#     profiles = []
#     for resource_id in bundle_id_resource_ids:
#         self.logger.info(f'Get provisioning profiles for {resource_id}')
#         try:
#             _profiles = self.api_client.bundle_ids.list_profiles(
#                 bundle_id=resource_id, resource_filter=profiles_filter)
#         except AppStoreConnectApiError as api_error:
#             raise AutomaticProvisioningError(str(api_error))
#         self.logger.info(f'Found {len(_profiles)} provisioning profiles matching {profiles_filter}')
#         if not _profiles:
#             not_found_message = f'Provisioning profiles for Bundle ID {resource_id} were not not found.'
#             self.logger.info(Colors.YELLOW(not_found_message))
#             if create_resource:
#                 self.logger.info('Create missing provisioning profile')
#                 self.logger.info(Colors.YELLOW('TODO...'))
#         profiles.extend(_profiles)
#
#     Profile.print_resources(profiles, json_output)
#     return profiles
#

#
# @cli.action('create-profile',
#             ProvisioningProfileActionArgument.PROFILE_NAME,
#             ProvisioningProfileActionArgument.PROFILE_TYPE,
#             BundleIdActionArgument.BUNDLE_ID_RESOURCE_ID,
#             CertificateActionArgument.CERTIFICATE_RESOURCE_IDS,
#             DeviceActionArgument.DEVICE_RESOURCE_IDS,
#             CommonActionArgument.JSON_OUTPUT)
# def create_profile(self,
#                    bundle_id_resource_id: ResourceId,
#                    profile_name: str,
#                    profile_type: ProfileType,
#                    certificate_resource_ids: List[ResourceId],
#                    device_resource_ids: Optional[List[ResourceId]] = None,
#                    json_output: bool = False) -> Profile:
#     """
#     Create provisioning profile.
#     """
#     self.logger.info(
#         f'Creating new {profile_type} Provisioning Profile "{profile_name}"')
#     try:
#         profile = self.api_client.profiles.create(
#             name=profile_name,
#             profile_type=profile_type,
#             bundle_id=bundle_id_resource_id,
#             certificates=certificate_resource_ids,
#             devices=device_resource_ids or []
#         )
#     except AppStoreConnectApiError as api_error:
#         raise AutomaticProvisioningError(str(api_error))
#     self.logger.info(f'Created Provisioning Profile {profile.id}')
#     profile.print(json_output)
#     return profile
#
# @cli.action('fetch-profiles',
#             ProvisioningProfileActionArgument.PROFILE_TYPE,
#             ProvisioningProfileActionArgument.PROFILE_STATE,
#             ProvisioningProfileActionArgument.PROFILE_NAME,
#             CommonActionArgument.CREATE_RESOURCE,
#             CommonActionArgument.JSON_OUTPUT,
#             CommonActionArgument.SAVE)
# def fetch_profiles(self,
#                     profile_type: Optional[ProfileType] = None,
#                     profile_state: Optional[ProfileState] = None,
#                     profile_name: Optional[str] = None,
#                     create_resource: bool = CommonActionArgument.CREATE_RESOURCE.get_default(),
#                     json_output: bool = CommonActionArgument.JSON_OUTPUT.get_default(),
#                     save: bool = CommonActionArgument.SAVE.get_default(),
#                     print_resources: bool = True):
#     """
#     Fetch provisioning profiles from Apple Developer Portal for offline use
#     """
#     profile_filter = self.api_client.profiles.Filter(
#         profile_type=profile_type,
#         profile_state=profile_state,
#         name=profile_name)
#     profiles = self._list_resources(profile_filter, self.api_client.profiles.list, 'Provisioning Profiles')
#     if print_resources:
#         Profile.print_resources(profiles, json_output)
