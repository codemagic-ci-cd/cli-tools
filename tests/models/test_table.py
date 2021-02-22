from codemagic.models.table import Header
from codemagic.models.table import Line
from codemagic.models.table import Spacer
from codemagic.models.table import Table

_EXPECTED_DEFAULT_RENDER = """\
┌───────────────────────┐
│        Header         │
├─────────────┬─────────┤
│  row_1      │  key_1  │
├─────────────┼─────────┤
│  row_2      │  key_2  │
│  row_3      │  key_3  │
├─────────────┴─────────┤
│       Subheader       │
├─────────────┬─────────┤
│  row_4      │  key_4  │
└─────────────┴─────────┘
"""

_EXPECTED_HEADERLESS_TABLE = """\
┌─────────┬─────────┐
│  row_1  │  key_1  │
│  row_2  │  key_2  │
└─────────┴─────────┘
"""


_EXPECTED_CUSTOM_TABLE_1 = """\
+---------------------------+
|          Header           |
+---------------+-----------+
| < row_1     > | < key_1 > |
+---------------+-----------+
| < row_2     > | < key_2 > |
| < row_3     > | < key_3 > |
+---------------+-----------+
|         Subheader         |
+---------------+-----------+
| < row_4     > | < key_4 > |
+---------------+-----------+
"""

_EXPECTED_CUSTOM_TABLE_2 = """\
ooooooooooooooooooooooooo
o        Header         o
ooooooooooooooooooooooooo
o  row_1      o  key_1  o
ooooooooooooooooooooooooo
o  row_2      o  key_2  o
o  row_3      o  key_3  o
ooooooooooooooooooooooooo
o       Subheader       o
ooooooooooooooooooooooooo
"""


def test_default_table():
    table = Table([
        Header('Header'),
        Line('row_1', 'key_1'),
        Spacer(),
        Line('row_2', 'key_2'),
        Line('row_3', 'key_3'),
        Header('Subheader'),
        Line('row_4', 'key_4'),
    ], header_color=None)
    assert table.construct() == _EXPECTED_DEFAULT_RENDER


def test_headerless_table():
    table = Table([
        Line('row_1', 'key_1'),
        Line('row_2', 'key_2'),
    ], header_color=None)
    assert table.construct() == _EXPECTED_HEADERLESS_TABLE


def test_custom_table_1():
    table = Table(
        [
            Header('Header'),
            Line('row_1', 'key_1'),
            Spacer(),
            Line('row_2', 'key_2'),
            Line('row_3', 'key_3'),
            Header('Subheader'),
            Line('row_4', 'key_4'),
        ],
        header_color=None,
        vertical_separator='|',
        horizontal_separator='-',
        horizontal_hinges=('+', '+', '+'),
        vertical_hinges=('+', '+'),
        corners=('+', '+', '+', '+'),
        left_padding=' < ',
        right_padding=' > ',
    )
    rendered = table.construct()
    assert rendered == _EXPECTED_CUSTOM_TABLE_1


def test_custom_table_2():
    table = Table(
        [
            Header('Header'),
            Line('row_1', 'key_1'),
            Spacer(),
            Line('row_2', 'key_2'),
            Line('row_3', 'key_3'),
            Header('Subheader'),
        ],
        header_color=None,
        vertical_separator='o',
        horizontal_separator='o',
        horizontal_hinges=('o', 'o', 'o'),
        vertical_hinges=('o', 'o'),
        corners=('o', 'o', 'o', 'o'),
    )
    assert table.construct() == _EXPECTED_CUSTOM_TABLE_2
