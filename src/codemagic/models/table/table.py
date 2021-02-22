from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from codemagic.cli import Colors

from .line import Header
from .line import Line
from .line import Spacer


class Table:

    def __init__(self,
                 lines: List[Line],
                 vertical_separator: str = '│',
                 horizontal_separator: str = '─',
                 horizontal_hinges: Tuple[str, str, str] = ('┼', '┴', '┬'),
                 vertical_hinges: Tuple[str, str] = ('├', '┤'),
                 corners: Tuple[str, str, str, str] = ('┌', '┐', '└', '┘'),
                 left_padding: str = '  ',
                 right_padding: str = '  ',
                 align_keys_left: bool = True,
                 align_values_left: bool = True,
                 header_color: Optional[Colors] = Colors.BOLD):
        self.lines = lines or []
        self.vertical_separator = vertical_separator
        self.horizontal_separator = horizontal_separator
        self.horizontal_hinges = horizontal_hinges
        self.vertical_hinges = vertical_hinges
        self.corners = corners
        self.left_padding = left_padding
        self.right_padding = right_padding
        self.align_keys_left = align_keys_left
        self.align_values_left = align_values_left
        self.header_color = header_color

    def get_max_key_width(self) -> int:
        return max(line.key_length for line in self.lines)

    def get_max_value_width(self) -> int:
        return max(line.value_length for line in self.lines)

    @classmethod
    def _get_header_paddings(cls, header, width: int) -> Tuple[str, str]:
        left_padding = ' ' * max(0, (width - len(header)) // 2)
        right_padding = ' ' * max(0, width - len(left_padding) - len(header))
        return left_padding, right_padding

    def _get_spacer(self, prev_line: Optional[Line], next_line: Optional[Line], keys_width: int,
                    total_width: int) -> str:
        if all([prev_line and prev_line.is_content_line(), next_line and next_line.is_content_line()]):
            hinge = self.horizontal_hinges[0]
        elif prev_line and prev_line.is_content_line():
            hinge = self.horizontal_hinges[1]
        elif next_line and next_line.is_content_line():
            hinge = self.horizontal_hinges[2]
        else:
            hinge = self.horizontal_separator

        lh, rh = self.vertical_hinges
        default_spacer = f'{lh}{total_width * self.horizontal_separator}{rh}'
        left = len(self.left_padding) + keys_width + len(self.right_padding)
        return f'{default_spacer[:left + 1]}{hinge}{default_spacer[left + 2:]}'

    def _get_header(self, line: Header, total_width: int):
        header = line.get_header()
        lp, rp = self._get_header_paddings(header, total_width)
        colored_header = self.header_color(header) if self.header_color else header
        return f'{self.vertical_separator}{lp}{colored_header}{rp}{self.vertical_separator}'

    def _get_line(self, line: Line, keys_width: int, values_width: int):
        key = line.get_key(keys_width, align_left=self.align_keys_left)
        value = line.get_value(values_width, align_left=self.align_values_left)
        key = f'{self.left_padding}{key}{self.right_padding}'
        value = f'{self.left_padding}{value}{self.right_padding}'
        return f'{self.vertical_separator}{key}{self.vertical_separator}{value}{self.vertical_separator}'

    def _adjust_corners(self, result: List[str]):
        tl, tr, bl, br = self.corners
        result[0] = f'{tl}{result[0][1:-1]}{tr}'
        result[-1] = f'{bl}{result[-1][1:-1]}{br}'

    def _iter_lines(self) -> Iterator:
        lines: List[Line] = []
        for line in self.lines:
            if isinstance(line, Header):
                lines.extend([Spacer(), line, Spacer()])
            else:
                lines.append(line)
        if not isinstance(lines[0], Spacer):
            lines.insert(0, Spacer())
        if not isinstance(lines[-1], Spacer):
            lines.append(Spacer())

        previous_lines = [None, *lines[:-1]]
        current_lines = lines
        next_lines = [*lines[1:], None]
        for _lines in zip(previous_lines, current_lines, next_lines):
            yield _lines

    def construct(self) -> str:
        keys_width = self.get_max_key_width()
        values_width = self.get_max_value_width()
        total_width = sum([
            keys_width,
            values_width,
            2 * len(self.left_padding),
            2 * len(self.right_padding),
            1,  # spacer in the middle
        ])

        result: List[str] = []
        for prev_line, line, next_line in self._iter_lines():
            if isinstance(line, Spacer):
                result.append(self._get_spacer(prev_line, next_line, keys_width, total_width))
            elif isinstance(line, Header):
                result.append(self._get_header(line, total_width))
            else:
                result.append(self._get_line(line, keys_width, values_width))

        self._adjust_corners(result)
        result.append('')

        return '\n'.join(result)
