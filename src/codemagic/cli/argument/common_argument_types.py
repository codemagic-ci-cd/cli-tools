import argparse
import json
import pathlib
from datetime import datetime
from typing import Dict


class CommonArgumentTypes:

    @staticmethod
    def maybe_dir(path_str: str) -> pathlib.Path:
        path = pathlib.Path(path_str).expanduser().absolute().resolve()
        if path.is_dir():
            # Existing directory
            return path
        elif path.exists():
            # Existing path that is not a directory
            raise argparse.ArgumentTypeError(f'Path "{path}" exists but is not a directory')
        elif any(parent.exists() and not parent.is_dir() for parent in path.parents):
            # Some of the parents is a file, directory cannot be created to this path
            raise argparse.ArgumentTypeError((
                f'Path "{path}" cannot be used as a directory as '
                'it contains a path to an existing file'
            ))
        else:
            # Either none of the parents exist, or some of them are directories
            return path

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
    def non_existing_path(path_str: str) -> pathlib.Path:
        path = pathlib.Path(path_str).expanduser()
        if not path.exists():
            return path
        raise argparse.ArgumentTypeError(f'Path "{path}" already exists')

    @staticmethod
    def json_dict(json_dict: str) -> Dict:
        try:
            d = json.loads(json_dict)
        except ValueError:
            raise argparse.ArgumentTypeError(f'"{json_dict}" is not a valid JSON')

        if not isinstance(d, dict):
            raise argparse.ArgumentTypeError(f'"{json_dict}" is not a dictionary')
        return d

    @staticmethod
    def iso_8601_datetime(iso_8601_timestamp: str) -> datetime:
        """
        Parse ISO8601 timestamp to datetime instance. Accept timestamps
        with and without the milliseconds portion. For example:
        '2020-08-04T11:44:12.000+0000' and '2021-01-28T06:01:32-08:00'.
        """
        datetime_formats = (
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y%m%dT%H%M%S%z',
        )
        for datetime_format in datetime_formats:
            try:
                return datetime.strptime(iso_8601_timestamp, datetime_format)
            except ValueError:
                continue
        raise argparse.ArgumentTypeError(f'"{iso_8601_timestamp}" is not a valid ISO 8601 timestamp')
