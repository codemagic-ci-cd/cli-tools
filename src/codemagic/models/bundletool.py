from pathlib import Path


class Bundletool:
    DOWNLOAD_URL = 'https://github.com/google/bundletool/releases/download/0.7.2/bundletool-all-0.7.2.jar'
    DEFAULT_PATH = Path('~/programs/bundletool-all-0.7.2.jar').expanduser()

    def __init__(self):
        pass
