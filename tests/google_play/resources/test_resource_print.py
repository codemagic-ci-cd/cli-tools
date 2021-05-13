from __future__ import annotations

from textwrap import dedent

from codemagic.google_play.resources import Track


def test_track_string(api_track):
    track = Track(**api_track)
    expected_output = dedent("""
        Track: internal
        Releases: [
            Status: draft
            Name: 29 (1.0.29)
            Version codes: [
                29
            ]

            Status: completed
            Name: trying2
            Version codes: [
                26
            ]
            Release notes: [
                Language: en-US
                Text: trying2
            ]
        ]""")
    assert str(track).replace('\t', '    ') == expected_output
