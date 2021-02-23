class GooglePlayDeveloperAPIClientError(Exception):
    pass


class CredentialsError(GooglePlayDeveloperAPIClientError):
    def __init__(self):
        super().__init__('Unable to parse service account credentials, must be a valid json')


class AuthorizationError(GooglePlayDeveloperAPIClientError):
    def __init__(self, reason: str):
        super().__init__(f'Unable to authorize with provided credentials. {reason}')


class EditError(GooglePlayDeveloperAPIClientError):
    def __init__(self, action: str, package_name: str, reason: str):
        super().__init__(f'Unable to {action} an edit for package "{package_name}". {reason}')


class VersionCodeFromTrackError(GooglePlayDeveloperAPIClientError):
    def __init__(self, track: str, reason: str):
        super().__init__(
            f'Failed to get version code from Google Play from {track} track. {reason}')
