from pathlib import Path


class Bundletool:
    DOWNLOAD_URL = 'https://github.com/google/bundletool/releases/download/0.11.0/bundletool-all-0.11.0.jar'
    DEFAULT_PATH = Path('/usr/local/bin/bundletool.jar').expanduser()

    def __init__(self):
        pass
