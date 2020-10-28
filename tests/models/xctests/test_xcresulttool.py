import json
import pathlib

import pytest

from codemagic.models.xctests.xcresulttool import XcResultTool


@pytest.mark.parametrize('xcresult_path', [
    pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-8.xcresult').expanduser(),
    pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-11.xcresult').expanduser(),
    pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-merged.xcresult').expanduser(),
])
def test_get_bundle(xcresult_path):
    result_path = xcresult_path.parent / f'{xcresult_path.stem}.json'
    with result_path.open('w') as fd:
        bundle = XcResultTool.get_bundle(xcresult_path)
        json.dump(bundle, fd)


def test_merge():
    input_paths = [
        pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-8.xcresult').expanduser(),
        pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-11.xcresult').expanduser(),
    ]
    output_path = pathlib.Path('~/xcode_test_results/Test-banaan-iPhone-merged.xcresult').expanduser()
    merged = XcResultTool.merge(*input_paths)
    merged.rename(output_path)
