from abc import ABC


class GoogleError(Exception, ABC):
    pass


class GoogleAuthenticationError(GoogleError):
    def __init__(self, message: str):
        super().__init__(f"Unable to authenticate with provided credentials. {message}")


class GoogleCredentialsError(GoogleError):
    def __init__(self, message: str):
        super().__init__(f"Invalid credentials. {message}")


class GoogleClientError(GoogleError):
    def __init__(self, message: str):
        super().__init__(f"Client error. {message}")


class GoogleHttpError(GoogleError):
    def __init__(self, message: str):
        super().__init__(message)
