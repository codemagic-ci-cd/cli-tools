from pathlib import Path


class ProvisioningProfile:

    DEFAULT_LOCATION = Path.home() / Path('Library', 'MobileDevice', 'Provisioning Profiles')

    def __init__(self):
        pass
