class GooglePlayDeveloperAPIClientError(Exception):
    pass


class CredentialsError(GooglePlayDeveloperAPIClientError):
    def __init__(self):
        super().__init__('Unable to parse service account credentials, must be a valid json')


class AuthorizationError(GooglePlayDeveloperAPIClientError):
    def __init__(self, reason):
        super().__init__(f'Unable to authorize with provided credentials. {reason}')


class EditError(GooglePlayDeveloperAPIClientError):
    def __init__(self, action, package_name, reason):
        super().__init__(f'Unable to {action} an edit for package "{package_name}". {reason}')


class VersionCodeFromTrackError(GooglePlayDeveloperAPIClientError):
    def __init__(self, package_name, track, reason):
        super().__init__(f'Failed to get version code from Google Play for package {package_name} from {track} track. {reason}')
