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


@pytest.mark.parametrize('buffer_size', [2**i for i in range(5, 15)])
def test_backwards_file_reader(buffer_size, random_lines):
    with tempfile.NamedTemporaryFile(mode='w') as tf:
        for i, line in enumerate(random_lines, 1):
            # Do not write double line break in the very end
            line_end = '\n' if i < len(random_lines) else ''
            tf.write(f'{line}{line_end}')
        tf.flush()

        iterator = iter_backwards(tf.name, buffer_size)
        backwards_lines = list(iterator)

    assert list(reversed(backwards_lines)) == random_lines
