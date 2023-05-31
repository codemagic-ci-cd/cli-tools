from abc import ABC


class GoogleBaseError(Exception, ABC):
    pass


class GoogleAuthenticationError(GoogleBaseError):
    def __init__(self, message: str):
        super().__init__(f'Unable to authenticate with provided credentials. {message}')


class GoogleCredentialsError(GoogleBaseError):
    def __init__(self, message: str):
        super().__init__(f'Invalid credentials. {message}')


class GoogleClientError(GoogleBaseError):
    def __init__(self, message: str):
        super().__init__(f'Client error. {message}')


class GoogleApiHttpError(GoogleBaseError):
    def __init__(self, message: str):
        super().__init__(f'Failed to communicate with Google. {message}')
