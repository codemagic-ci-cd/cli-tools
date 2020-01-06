import logging
import pathlib
import sys
import tempfile
from datetime import datetime
from typing import IO
from typing import Type

_BASE_LOGGER = logging.getLogger('codemagic-cli-tools-base-logger')
Logger = logging.Logger


def get_log_path() -> pathlib.Path:
    tmp_dir = pathlib.Path('/tmp')
    if not tmp_dir.is_dir():
        tmp_dir = pathlib.Path(tempfile.gettempdir())
    date = datetime.now().strftime('%d-%m-%y')
    return tmp_dir / f'codemagic-{date}.log'


def _setup_stream_log_handler(
        stream: IO = sys.stderr,
        verbose: bool = False,
        enable_logging: bool = True) -> logging.Handler:
    if verbose:
        fmt = '[%(asctime)s] %(levelname)-5s > %(message)s'
        level = logging.DEBUG
    elif not enable_logging:
        fmt = '%(message)s'
        level = logging.ERROR
    else:
        fmt = '%(message)s'
        level = logging.INFO

    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter(fmt, '%H:%M:%S')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def _setup_file_log_handler() -> logging.Handler:
    fmt = '[%(asctime)s] %(levelname)-5s %(filename)s:%(lineno)d > %(message)s'
    formatter = logging.Formatter(fmt, '%H:%M:%S %d-%m-%Y')
    path = get_log_path()
    handler = logging.FileHandler(path)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def _get_logger_name(base_name: str, file_logging: bool, stream_logging: bool) -> str:
    choices = ((file_logging, 'File'), (stream_logging, 'Stream'))
    middle = ''.join(name for log, name in choices if log)
    return f'{base_name}{middle}Logger'


def get_printer(klass: Type):
    printer = logging.getLogger(f'{klass.__name__}Printer')

    printer.setLevel(logging.DEBUG)

    file_handlers = [h for h in _BASE_LOGGER.handlers if isinstance(h, logging.FileHandler)]
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    printer.addHandler(file_handlers[0])
    printer.addHandler(stream_handler)

    return printer


def get_logger(klass: Type, *, log_to_file: bool = True, log_to_stream: bool = True) -> logging.Logger:
    logger_name = _get_logger_name(klass.__name__, log_to_file, log_to_stream)
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    if log_to_file:
        file_handlers = [h for h in _BASE_LOGGER.handlers if isinstance(h, logging.FileHandler)]
        logger.addHandler(file_handlers[0])
    if log_to_stream:
        stream_handlers = [h for h in _BASE_LOGGER.handlers if isinstance(h, logging.StreamHandler)]
        logger.addHandler(stream_handlers[0])

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

    stream_handler = _setup_stream_log_handler(stream, verbose, enable_logging)
    file_handler = _setup_file_log_handler()
    _BASE_LOGGER.addHandler(stream_handler)
    _BASE_LOGGER.addHandler(file_handler)
