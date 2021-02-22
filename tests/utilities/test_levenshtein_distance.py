import pytest

from codemagic.utilities.levenshtein_distance import levenshtein_distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('', '', 0),
    ('a', '', 1),
    ('', 'a', 1),
    ('abc', '', 3),
    ('', 'abc', 3),
])
def test_levenshtein_distance_on_empty_strings(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('', '', 0),
    ('a', 'a', 0),
    ('abc', 'abc', 0),
])
def test_levenshtein_distance_on_equal_strings(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('', 'a', 1),
    ('a', 'ab', 1),
    ('b', 'ab', 1),
    ('ac', 'abc', 1),
    ('abcdefg', 'xabxcdxxefxgx', 6),
])
def test_levenshtein_distance_on_inserts(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('a', '', 1),
    ('ab', 'a', 1),
    ('ab', 'b', 1),
    ('abc', 'ac', 1),
    ('xabxcdxxefxgx', 'abcdefg', 6),
])
def test_levenshtein_distance_on_removals(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('a', 'b', 1),
    ('ab', 'ac', 1),
    ('ac', 'bc', 1),
    ('abc', 'axc', 1),
    ('xabxcdxxefxgx', '1ab2cd34ef5g6', 6),
])
def test_levenshtein_distance_on_substitutions(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('example', 'samples', 3),
    ('sturgeon', 'urgently', 6),
    ('levenshtein', 'frankenstein', 6),
    ('distance', 'difference', 5),
    ('java was neat', 'scala is great', 7),
])
def test_levenshtein_distance_on_all_operations(s1, s2, distance):
    assert levenshtein_distance(s1, s2) == distance
