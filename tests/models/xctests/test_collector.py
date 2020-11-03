from pathlib import Path
from typing import List
from unittest import mock

import pytest

from codemagic.models.xctests import XcResultCollector
from codemagic.models.xctests import XcResultTool


@pytest.fixture()
def collector():
    return XcResultCollector()


def _create_mock_results(result_paths: List[Path]) -> List[Path]:
    for result_path in result_paths:
        result_path.mkdir(parents=True)
    return result_paths


def test_collect_result(collector, temp_dir):
    xcresults = _create_mock_results([
        Path(temp_dir, 'a', 'result-1.xcresult'),
        Path(temp_dir, 'a', 'result-2.xcresult'),
        Path(temp_dir, 'a', 'result-3.xcresult'),
        Path(temp_dir, 'b', 'c', 'result.xcresult'),
        Path(temp_dir, 'result-0.xcresult'),
    ])
    collected_results = collector.gather_results(temp_dir).get_collected_results()
    assert collected_results == xcresults


def test_ignore_results(collector, temp_dir):
    _create_mock_results([
        Path(temp_dir, 'a', 'result-1.xcresult'),
        Path(temp_dir, 'a', 'result-2.xcresult'),
        Path(temp_dir, 'b', 'c', 'result-1.xcresult'),
        Path(temp_dir, 'result-0.xcresult'),
    ])
    collector.ignore_results(temp_dir)
    xcresults = _create_mock_results([
        Path(temp_dir, 'a', 'result-1-1.xcresult'),
        Path(temp_dir, 'a', 'result-2-1.xcresult'),
        Path(temp_dir, 'b', 'c', 'result-1-1.xcresult'),
        Path(temp_dir, 'result-0-1.xcresult'),
    ])
    collected_results = collector.gather_results(temp_dir).get_collected_results()
    assert collected_results == xcresults


def test_merge_results_one_result(collector, temp_dir):
    xcresult = _create_mock_results([Path(temp_dir, 'result.xcresult')])[0]
    merged_result = collector.gather_results(temp_dir).get_merged_xcresult()
    assert xcresult == merged_result
    assert collector._xcresult_is_merged is False
    assert collector._xcresult == merged_result


@pytest.mark.parametrize('relative_paths, expected_result_prefix', [
    (['result-1-a.xcresult', 'result-1-b.xcresult', 'a/b/result-1-c.xcresult'], 'result-1-'),
    (['a.xcresult', 'b.xcresult', 'a/b/c.xcresult'], 'Test-'),
])
def test_merge_results(relative_paths, expected_result_prefix, collector, temp_dir):
    _create_mock_results([Path(temp_dir, relative) for relative in relative_paths])
    with mock.patch.object(XcResultTool, '_run_command', lambda args, error: ''):
        merged_result = collector.gather_results(temp_dir).get_merged_xcresult()
    assert merged_result.name.startswith(expected_result_prefix)
    assert merged_result.stem.endswith('-merged')
    assert merged_result.suffix == '.xcresult'
    assert collector._xcresult_is_merged is True
    assert collector._xcresult == merged_result


@mock.patch('codemagic.models.xctests.collector.shutil.rmtree')
def test_forget_merged_result_no_merged_result(mock_rmtree, collector):
    collector._xcresult = None
    collector._xcresult_is_merged = False
    collector.forget_merged_result()
    assert mock_rmtree.call_count == 0


@mock.patch('codemagic.models.xctests.collector.shutil.rmtree')
@pytest.mark.parametrize('xcresult, is_merged, removals', [
    (None, False, 0),
    (Path('result.xcresult'), False, 0),
    (Path('result.xcresult'), True, 1),
])
def test_forget_merged_result_result_not_merged(mock_rmtree, collector, xcresult, is_merged, removals):
    collector._xcresult = xcresult
    collector._xcresult_is_merged = is_merged
    collector.forget_merged_result()
    assert mock_rmtree.call_count == removals
    if removals > 0:
        assert mock_rmtree.call_args[0][0] == xcresult
