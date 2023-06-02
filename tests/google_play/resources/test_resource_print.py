from __future__ import annotations

from codemagic.google_play.resources import Track


def test_track_string(api_track):
    track = Track(**api_track)
    expected_output = (
        '\n'
        'Track: internal\n'
        'Releases: [\n'
        '    Status: draft\n'
        '    Name: 29 (1.0.29)\n'
        '    Version codes: [\n'
        '        29\n'
        '    ]\n'
        '\n'
        '    Status: completed\n'
        '    Name: trying2\n'
        '    Version codes: [\n'
        '        26\n'
        '    ]\n'
        '    Release notes: [\n'
        '        Language: en-US\n'
        '        Text: trying2\n'
        '    ]\n'
        ']'
    ).replace(4*' ', '\t')
    assert str(track) == expected_output
