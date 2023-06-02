import io
import random
import string
import tempfile

import pytest

from codemagic.utilities.backwards_file_reader import iter_backwards


@pytest.fixture
def random_lines():
    lines = []
    for c in (string.ascii_letters + string.digits):
        lines.extend([random.randint(80, 10000) * c, ''])
    return lines


def _write_file_contents(file_descriptor, lines):
    for i, line in enumerate(lines, 1):
        # Do not write double line break in the very end
        line_end = '\n' if i < len(lines) else ''
        file_descriptor.write(f'{line}{line_end}')


@pytest.mark.parametrize('buffer_size', [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_path(buffer_size, random_lines):
    with tempfile.NamedTemporaryFile(mode='w') as tf:
        _write_file_contents(tf, random_lines)
        tf.flush()

        iterator = iter_backwards(tf.name, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize('buffer_size', [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_in_memory_file(buffer_size, random_lines):
    with tempfile.TemporaryFile(mode='r+') as tf:
        _write_file_contents(tf, random_lines)
        tf.flush()

        iterator = iter_backwards(tf, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize('buffer_size', [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_stringio(buffer_size, random_lines):
    sio = io.StringIO()
    _write_file_contents(sio, random_lines)

    iterator = iter_backwards(sio, buffer_size)
    backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines
