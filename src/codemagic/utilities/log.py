import logging
import os
import pathlib
import sys
import tempfile
from datetime import datetime
from typing import IO
from typing import Optional
from typing import Type

Logger = logging.Logger


class LogHandlers:
    stream_fmt = '%(message)s'
    stream_fmt_verbose = '[%(asctime)s] %(levelname)-5s > %(message)s'
    file_fmt = '[%(asctime)s] %(levelname)-5s %(filename)s:%(lineno)d > %(message)s'

    _stream_handler: Optional[logging.StreamHandler] = None
    _file_handler: Optional[logging.FileHandler] = None

    @classmethod
    def configure_stream_handler(cls,
                                 stream: IO = sys.stderr,
                                 verbose: bool = False,
                                 enable_logging: bool = True) -> logging.StreamHandler:
        fmt = cls.stream_fmt
        if verbose:
            fmt = cls.stream_fmt_verbose
            level = logging.DEBUG
        elif not enable_logging:
            level = logging.ERROR
        else:
            level = logging.INFO

        stream_formatter = logging.Formatter(fmt, '%H:%M:%S')
        cls._stream_handler = logging.StreamHandler(stream)
        cls._stream_handler.setLevel(level)
        cls._stream_handler.setFormatter(stream_formatter)
        return cls._stream_handler

    @classmethod
    def configure_file_handler(cls) -> logging.FileHandler:
        file_formatter = logging.Formatter(cls.file_fmt, '%H:%M:%S %d-%m-%Y')
        cls._file_handler = logging.FileHandler(get_log_path())
        cls._file_handler.setLevel(logging.DEBUG)
        cls._file_handler.setFormatter(file_formatter)
        return cls._file_handler

    @classmethod
    def get_file_handler(cls) -> logging.FileHandler:
        return cls._file_handler or cls.configure_file_handler()

    @classmethod
    def get_stream_handler(cls) -> logging.StreamHandler:
        return cls._stream_handler or cls.configure_stream_handler(enable_logging=False)


def get_log_path() -> pathlib.Path:
    tmp_dir = pathlib.Path(tempfile.gettempdir())
    date = datetime.now().strftime('%d-%m-%y')

    if os.environ.get('PYTEST_RUN_CONFIG', False):
        # Use different log file when tests are running
        log_path = tmp_dir / f'codemagic-{date}-tests.log'
    else:
        log_path = tmp_dir / f'codemagic-{date}.log'

    return log_path


def _get_logger_name(base_name: str, file_logging: bool, stream_logging: bool) -> str:
    choices = ((file_logging, 'File'), (stream_logging, 'Stream'))
    middle = ''.join(name for log, name in choices if log)
    return f'{base_name}{middle}Logger'


def get_printer(klass: Type):
    from codemagic.cli import CliApp

    printer = logging.getLogger(f'{klass.__name__}Printer')

    printer.setLevel(logging.DEBUG)
    printer.addHandler(LogHandlers.get_file_handler())

    if CliApp.is_cli_invocation():
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(stream_formatter)
        printer.addHandler(stream_handler)

    return printer


def get_logger(klass: Type, *, log_to_file: bool = True, log_to_stream: bool = True) -> logging.Logger:
    logger_name = _get_logger_name(klass.__name__, log_to_file, log_to_stream)
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    if log_to_file:
        logger.addHandler(LogHandlers.get_file_handler())
    if log_to_stream:
        logger.addHandler(LogHandlers.get_stream_handler())
    if not log_to_stream and not log_to_file:
        logger.addHandler(logging.NullHandler())

    return logger


def get_stream_logger(klass: Type) -> logging.Logger:
    return get_logger(klass, log_to_file=False, log_to_stream=True)


def get_file_logger(klass: Type) -> logging.Logger:
    return get_logger(klass, log_to_file=True, log_to_stream=False)


def initialize_logging(
        stream: IO = sys.stderr,
        verbose: bool = False,
        enable_logging: bool = True):
    for logger_name in ('requests', 'urllib3'):
        requests_logger = logging.getLogger(logger_name)
        requests_logger.setLevel(logging.ERROR)

    LogHandlers.configure_stream_handler(stream, verbose, enable_logging)
    LogHandlers.configure_file_handler()
