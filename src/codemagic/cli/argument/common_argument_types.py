import argparse
import pathlib


class CommonArgumentTypes:

    @staticmethod
    def existing_path(path_str: str) -> pathlib.Path:
        path = pathlib.Path(path_str).expanduser()
        if path.exists():
            return path
        raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')
