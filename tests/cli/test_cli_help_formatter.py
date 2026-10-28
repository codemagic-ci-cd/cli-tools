import argparse

from codemagic.cli.cli_help_formatter import CliHelpFormatter


def _format_description(description: str) -> str:
    parser = argparse.ArgumentParser(description=description, formatter_class=CliHelpFormatter)
    return parser.format_help()


def test_description_paragraphs_are_kept_apart():
    description = "First line\nwrapped here.\n\nSecond paragraph.\n\nThird paragraph."
    help_text = _format_description(description)
    assert "First line wrapped here.\n\nSecond paragraph.\n\nThird paragraph.\n" in help_text


def test_description_without_blank_lines_is_reflowed():
    help_text = _format_description("Single paragraph\nwrapped over\nthree lines.")
    assert "Single paragraph wrapped over three lines.\n" in help_text
