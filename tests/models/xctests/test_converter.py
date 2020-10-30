import pathlib
from xml.dom import minidom
from xml.etree import ElementTree

import pytest

from codemagic.models.junit import TestSuites
from codemagic.models.xctests.collector import XcResultCollector
from codemagic.models.xctests.converter import XcResultConverter
from codemagic.models.xctests.xcresult import ActionsInvocationRecord


@pytest.mark.skip('Test is not ready')
def test_parser():
    results_dir = pathlib.Path('~/xcode_test_results/for_tests').expanduser()
    xcresult = XcResultCollector().gather_results(results_dir).choose_xcresult()
    actions_invocation_record = ActionsInvocationRecord.from_xcresult(xcresult)
    test_suites: TestSuites = XcResultConverter.xcresult_to_junit(actions_invocation_record)
    xml_str = ElementTree.tostring(test_suites.as_xml())
    print('\n', minidom.parseString(xml_str).toprettyxml())
