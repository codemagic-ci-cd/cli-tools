from __future__ import annotations

import textwrap

from codemagic.google.resources.firebase import Release


def test_release_initialization(api_firebase_release: dict):
    release = Release(**api_firebase_release)
    assert release.dict() == api_firebase_release


def test_release_string_representation(api_firebase_release: dict):
    release = Release(**api_firebase_release)
    expected = textwrap.dedent(
        """
        Name: projects/146661841143/apps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8
        Display version: 1.0
        Build version: 1
        Create time: 2025-02-12T14:12:59.510381+00:00
        Firebase console URI: https://console.firebase.google.com/project/codemagic-cli-tools-test-app/appdistribution/app/android:io.codemagic.cli_tools_firebase/releases/78ruoe1t1uvr8
        Testing URI: https://appdistribution.firebase.google.com/testerapps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8
        Binary download URI: https://firebaseappdistribution.googleapis.com/app-binary-downloads/projects/146661841143/apps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8/binaries/fcdd844be2bd504ae7bb9d672731ddbfcd89c1419a9aa746a0bb6f67d3a1429d/app.apk?token=token
        Release notes:
            Text: My release notes""",
    ).strip()
    assert str(release) == expected
