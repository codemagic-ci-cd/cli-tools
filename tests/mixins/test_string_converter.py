import pytest

from codemagic.mixins import StringConverterMixin


@pytest.mark.parametrize('bytes_or_str, expected_result', [
    ('', b''),
    ('test', b'test'),
    ('á', b'\xc3\xa1'),
    ('Привет, мир', b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82, \xd0\xbc\xd0\xb8\xd1\x80'),
    (r'¯\_( ͡° ͜ʖ ͡°)_/¯', b'\xc2\xaf\\_( \xcd\xa1\xc2\xb0 \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)_/\xc2\xaf'),
    ('🤩', b'\xf0\x9f\xa4\xa9'),
    (b'\xf0\x9f\xa4\xa9', b'\xf0\x9f\xa4\xa9'),
    (b'', b''),
    (b'test', b'test'),
])
def test_to_bytes(bytes_or_str, expected_result):
    assert StringConverterMixin._bytes(bytes_or_str) == expected_result


@pytest.mark.parametrize('bytes_or_str, expected_result', [
    ('', ''),
    ('test', 'test'),
    (b'\xc3\xa1', 'á'),
    (b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82, \xd0\xbc\xd0\xb8\xd1\x80', 'Привет, мир'),
    (b'\xc2\xaf\\_( \xcd\xa1\xc2\xb0 \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)_/\xc2\xaf', r'¯\_( ͡° ͜ʖ ͡°)_/¯'),
    (b'\xf0\x9f\xa4\xa9', '🤩'),
    ('🤩', '🤩'),
    (b'', ''),
    (b'test', 'test'),
])
def test_to_str(bytes_or_str, expected_result):
    assert StringConverterMixin._str(bytes_or_str) == expected_result
