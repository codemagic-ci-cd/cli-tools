import random
import string
import tempfile

import pytest

from codemagic.models.backwards_file_reader import BackwardsFileReader


@pytest.mark.parametrize('buffer_size', [2**i for i in range(5, 15)])
def test_backwards_file_reader(buffer_size):
    lines = [random.randint(80, 10000) * c for c in (string.ascii_letters + string.digits)]
    with tempfile.NamedTemporaryFile(mode='w') as tf:
        for line in lines:
            tf.write(f'{line}\n')
        tf.flush()

        reader = BackwardsFileReader(tf.name, buffer_size)
        backwards_lines = list(reader.iter_backwards())

    assert backwards_lines == list(reversed(lines))
