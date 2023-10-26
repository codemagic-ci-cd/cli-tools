import io
import random
import string
import tempfile

import pytest
from codemagic.utilities.backwards_file_reader import iter_backwards


@pytest.fixture
def random_lines():
    lines = []
    for c in string.ascii_letters + string.digits:
        lines.extend([random.randint(80, 10000) * c, ""])
    return lines


@pytest.mark.parametrize("buffer_size", [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_path(buffer_size, random_lines):
    with tempfile.NamedTemporaryFile(mode="w") as tf:
        tf.write("\n".join(random_lines))
        tf.flush()

        iterator = iter_backwards(tf.name, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize("buffer_size", [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_in_memory_text_file(buffer_size, random_lines):
    with tempfile.TemporaryFile(mode="r+") as tf:
        tf.write("\n".join(random_lines))
        tf.flush()

        iterator = iter_backwards(tf, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize("buffer_size", [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_in_memory_binary_file(buffer_size, random_lines):
    with tempfile.TemporaryFile(mode="rb+") as tf:
        tf.write(b"\n".join(line.encode() for line in random_lines))
        tf.flush()

        iterator = iter_backwards(tf, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize("buffer_size", [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_stringio(buffer_size, random_lines):
    sio = io.StringIO("\n".join(random_lines))

    iterator = iter_backwards(sio, buffer_size)
    backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines


@pytest.mark.parametrize("buffer_size", [2**i for i in range(5, 15)])
def test_backwards_file_reader_with_binaryio(buffer_size, random_lines):
    bio = io.BytesIO(b"\n".join(line.encode() for line in random_lines))

    iterator = iter_backwards(bio, buffer_size)
    backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines
