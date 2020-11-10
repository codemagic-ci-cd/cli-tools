import argparse
import json
import pathlib
from typing import Dict


class CommonArgumentTypes:

    @staticmethod
    def existing_dir(path_str: str) -> pathlib.Path:
        path = pathlib.Path(path_str).expanduser()
        if path.is_dir():
            return path
        raise argparse.ArgumentTypeError(f'Path "{path}" is not a directory')

    @staticmethod
    def existing_path(path_str: str) -> pathlib.Path:
        path = pathlib.Path(path_str).expanduser()
        if path.exists():
            return path
        raise argparse.ArgumentTypeError(f'Path "{path}" does not exist')

    @staticmethod
    def json_dict(json_dict: str) -> Dict:
        try:
            d = json.loads(json_dict)
        except ValueError:
            raise argparse.ArgumentTypeError(f'"{json_dict}" is not a valid JSON')

        if not isinstance(d, dict):
            raise argparse.ArgumentTypeError(f'"{json_dict}" is not a dictionary')
        return d
