import pathlib
from typing import List
from xml.dom import minidom
from xml.etree import ElementTree

from codemagic.models import junit
from codemagic.models.xctests.parser import XcResultParser


def test_parser():
    test_suites: List[junit.TestSuite] = XcResultParser() \
        .gather_results(pathlib.Path('~/xcode_test_results/for_tests').expanduser()) \
        .parse_results()
    test_suites = junit.TestSuites(name='', test_suites=test_suites)
    xml_str = ElementTree.tostring(test_suites.to_xml())
    print('\n', minidom.parseString(xml_str).toprettyxml())
