from abc import ABC


class BaseError(Exception, ABC):
    pass


class AuthenticationError(BaseError):
    def __init__(self, message: str):
        super().__init__(f'Unable to authenticate with provided credentials. {message}')


class CredentialsError(BaseError):
    def __init__(self, message: str):
        super().__init__(f'Invalid Firebase credentials. {message}')


class ClientError(BaseError):
    def __init__(self, message: str):
        super().__init__(f'Client error. {message}')


class FirebaseApiHttpError(BaseError):
    def __init__(self, message: str):
        super().__init__(f'Failed to communicate with Firebase. {message}')
