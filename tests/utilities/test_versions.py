import pytest
from codemagic.utilities import versions
from packaging import version


def test_versions_sort_key():
    unsorted_versions = ["v2.3", "v1.0.73", "v.1.6.70", "v1.ÃŸ.69", "1.0.4", "1.0.0"]
    expected_sorted_versions = [
        "v1.ÃŸ.69",
        "1.0.0",
        "1.0.4",
        "v1.0.73",
        "v.1.6.70",
        "v2.3",
    ]
    assert sorted(unsorted_versions, key=versions.sorting_key) == expected_sorted_versions


@pytest.mark.parametrize(
    "given_version, expected_version",
    [
        ("1.0.0", version.Version("1.0.0")),
        ("1.0.4", version.Version("1.0.4")),
        ("v1.0.73", version.Version("1.0.73")),
        ("v.1.6.70", version.Version("1.6.70")),
        ("v2.3", version.Version("2.3")),
    ],
)
def test_parse_version(given_version, expected_version):
    parsed_version = versions.parse_version(given_version)
    assert parsed_version == expected_version


@pytest.mark.parametrize("given_version", ["v1.ÃŸ.69", "lorem ipsum", "-1"])
def test_parse_version_invalid_version(given_version):
    with pytest.raises(ValueError):
        versions.parse_version(given_version)


@pytest.mark.parametrize("given_version", [0, [], {}])
def test_parse_version_invalid_type(given_version):
    with pytest.raises(TypeError):
        versions.parse_version(given_version)  # type: ignore
