from distutils.version import LooseVersion

import pytest

from codemagic.models.simulator import Runtime


@pytest.mark.parametrize('raw_runtime_name, expected_runtime_version', [
    ('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2', '14.0.2'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-14-0', '14.0'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-12-4', '12.4'),
    ('com.apple.CoreSimulator.SimRuntime.watchOS-7-0-1-1', '7.0.1.1'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-13-2', '13.2'),
    ('com.apple.CoreSimulator.SimRuntime.iOS 10.2.3', '10.2.3'),
    ('iOS 14.2.1', '14.2.1'),
    ('iPhone Xr Max iOS 14.2.1', '14.2.1'),
    ('iOS 14.2.1 iPhone Xr Max ', '14.2.1'),
])
def test_get_runtime_version(raw_runtime_name, expected_runtime_version):
    runtime_version = Runtime(raw_runtime_name).runtime_version
    assert runtime_version == LooseVersion(expected_runtime_version)


@pytest.mark.parametrize('raw_runtime_name, expected_runtime_name', [
    ('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2', 'tvOS'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-14-0', 'iOS'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-12-4', 'iOS'),
    ('com.apple.CoreSimulator.SimRuntime.watchOS-7-0-1-1', 'watchOS'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-13-2', 'iOS'),
    ('iOS 13.2', 'iOS'),
    ('com.example.Something.watchOS 1.2.3', 'watchOS'),
])
def test_get_runtime_name(raw_runtime_name, expected_runtime_name):
    runtime_name = Runtime(raw_runtime_name).runtime_name
    assert runtime_name is Runtime.Name(expected_runtime_name)


def test_get_invalid_runtime_name():
    raw_runtime_name = 'not-a-valid-runtime'
    with pytest.raises(ValueError) as exception_info:
        _ = Runtime(raw_runtime_name).runtime_name
    error = exception_info.value
    assert str(error) == f"Invalid runtime '{raw_runtime_name}'"


@pytest.mark.parametrize('raw_runtime_name, expected_pretty_name', [
    ('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2', 'tvOS 14.0.2'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-14-0', 'iOS 14.0'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-12-4', 'iOS 12.4'),
    ('com.apple.CoreSimulator.SimRuntime.watchOS-7-0-1-1', 'watchOS 7.0.1.1'),
    ('com.apple.CoreSimulator.SimRuntime.iOS-13-2', 'iOS 13.2'),
    ('com.apple.CoreSimulator.SimRuntime.iOS 10.2.3', 'iOS 10.2.3'),
    ('iOS 14.2.1', 'iOS 14.2.1'),
])
def test_string_representation(raw_runtime_name, expected_pretty_name):
    assert str(Runtime(raw_runtime_name)) == expected_pretty_name


@pytest.mark.parametrize('first, second, expected_result', [
    (Runtime('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2'),
     Runtime('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2'), True),
    ('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2', Runtime('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2'), True),
    (Runtime('tvOS-14-0-2'), Runtime('com.apple.CoreSimulator.SimRuntime.tvOS-14-0-2'), True),
    (Runtime('tvOS-14-0-2'), Runtime('tvOS 14.0.2'), True),
    (Runtime('tvOS-14-0-2'), 'tvOS 14.0.2', True),
    ('tvOS 14.0.2', Runtime('tvOS-14-0-2'), True),
    (Runtime('iOS 13.1'), Runtime('iOS-13-1'), True),
    (Runtime('tvOS-14-0-2'), 'tvOS 14.0', False),
    ('tvOS 14.0.2', Runtime('tvOS-14-0'), False),
    (Runtime('iOS 13.1'), Runtime('iOS-13-2'), False),
    (Runtime('iOS 13.2'), Runtime('iOS 13.1'), False),
])
def test_equality(first, second, expected_result):
    comparison_result = first == second
    assert comparison_result is expected_result


@pytest.mark.parametrize('compare_to', [
    1, 1.0, 1j, object(), [], tuple(), set(), dict(),
])
def test_equality_to_invalid_type(compare_to):
    with pytest.raises(ValueError) as exception_info:
        _ = Runtime('iOS 1') == compare_to
    error = exception_info.value
    assert str(error) == f'Cannot compare {Runtime.__name__} with {compare_to.__class__.__name__}'


def test_total_ordering():
    expected_ordering = [
        'iOS 1.0.0',
        'iOS 1.0.1',
        'iOS 2.9.4',
        'iOS 2.10',
        'tvOS 4.1',
        'tvOS 7.2.1',
        'tvOS 7.2.2',
        'watchOS 6.1',
        'watchOS 6.1.0',
        'watchOS 6.1.1',
        'watchOS 7.2',
    ]
    ordered = sorted([
        'iOS 1.0.0',
        'watchOS 6.1.1',
        'iOS 2.9.4',
        'tvOS 7.2.2',
        'iOS 1.0.1',
        'watchOS 6.1',
        'watchOS 6.1.0',
        'tvOS 7.2.1',
        'tvOS 4.1',
        'watchOS 7.2',
        'iOS 2.10',
    ], key=Runtime)
    assert ordered == expected_ordering
