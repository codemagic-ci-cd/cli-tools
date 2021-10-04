import os
import subprocess
from tempfile import NamedTemporaryFile

from codemagic import cli


def assert_non_blocking(stream):
    try:
        import fcntl
    except ImportError:
        assert False, 'Failed to import module "fcntl"'
    stream_flags = fcntl.fcntl(stream.fileno(), fcntl.F_GETFL)
    assert stream_flags & os.O_NONBLOCK == os.O_NONBLOCK


def test_non_blocking_streams():
    cli_process = cli.CliProcess([])
    cli_process._process = subprocess.Popen(
        ['sleep', '3'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    cli_process._ensure_process_streams_are_non_blocking()

    assert_non_blocking(cli_process._process.stdout)
    assert_non_blocking(cli_process._process.stderr)

    cli_process._process.kill()


def test_non_blocking_streams_file_fd():
    with NamedTemporaryFile(mode='wb') as tf:
        cli_process = cli.CliProcess([])
        cli_process._process = subprocess.Popen(
            ['sleep', '3'],
            stdout=tf,
            stderr=tf)
        cli_process._ensure_process_streams_are_non_blocking()

        assert cli_process._process.stdout is None
        assert cli_process._process.stderr is None

        cli_process._process.kill()
