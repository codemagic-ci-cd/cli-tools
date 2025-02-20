from datetime import datetime
from datetime import timezone
from unittest import mock

import pytest

from codemagic.google.resources.firebase import Release
from codemagic.google.resources.firebase import ReleaseNotes


@pytest.fixture
def release():
    return Release(
        name="projects/146661841143/apps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8",
        releaseNotes=ReleaseNotes("My release notes"),
        displayVersion="1.0",
        buildVersion="1",
        createTime=datetime(2025, 2, 12, 14, 12, 59, 510381, tzinfo=timezone.utc),
        firebaseConsoleUri=mock.ANY,
        testingUri=mock.ANY,
        binaryDownloadUri=mock.ANY,
    )


@pytest.fixture
def release_response():
    return {
        "name": "projects/146661841143/apps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8",
        "releaseNotes": {"text": "My release notes"},
        "displayVersion": "1.0",
        "buildVersion": "1",
        "createTime": "2025-02-12T14:12:59.510381+00:00",
        "firebaseConsoleUri": "https://console.firebase.google.com/project/codemagic-cli-tools-test-app/appdistribution/app/android:io.codemagic.cli_tools_firebase/releases/78ruoe1t1uvr8",
        "testingUri": "https://appdistribution.firebase.google.com/testerapps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8",
        "binaryDownloadUri": "https://firebaseappdistribution.googleapis.com/app-binary-downloads/projects/146661841143/apps/1:146661841143:android:a8d456e0c8b5e71bd11bf2/releases/78ruoe1t1uvr8/binaries/fcdd844be2bd504ae7bb9d672731ddbfcd89c1419a9aa746a0bb6f67d3a1429d/app.apk?token=AFb1MRwAAAAAZ6y6163tUiOtYM88Px37dgSK9Ee41xTe2lPBDnfIysE5Bc4V1o18r159NXuUqMC9l3jiYiM3DqbTVGUhda5TsZr5FODKeE9gS47hRAKznZ7cXGaN9kDtjWqaWie4z0KmCw09qqN1xi1fROX9L0G-0TuQjGGmP344yfpFpZ8y9x8xdw0E_b_9OyCenNAMSuqs8Q2r6hMTr5dzSB34jCCOyj2Ue4EhhD1ybq56HJbR8MDfXnTUKxxZcuq1W1rBX847gRxQVAezzbh0Vrq0xvfV51VIs9lEAG1-VQOd_kITlbF5wTfp6XbpsBrQLOeZS_PWMRUAqihaHY2Kg3hi42Ftz5AXJBY",
    }
