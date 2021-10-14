import os
import subprocess
from tempfile import NamedTemporaryFile

import pytest

from codemagic import cli


def assert_non_blocking(stream):
    assert os.get_blocking(stream.fileno()) is False


@pytest.mark.skipif(os.name == 'nt', reason='Cannot run on Windows')
def test_non_blocking_streams():
    cli_process = cli.CliProcess([])
    cli_process._process = subprocess.Popen(
        ['sleep', '3'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    cli_process._configure_process_streams()

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
        cli_process._configure_process_streams()

        assert cli_process._process.stdout is None
        assert cli_process._process.stderr is None
        assert cli_process._stdout_stream is None
        assert cli_process._stderr_stream is None

        cli_process._process.kill()
