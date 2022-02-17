from codemagic import cli


class Password(cli.EnvironmentArgumentValue[str]):
    @classmethod
    def _is_valid(cls, value: str) -> bool:
        return True


class KeyPassword(Password):
    ...


class KeystorePassword(Password):
    ...


class KeyAlias(cli.EnvironmentArgumentValue[str]):
    ...
