#!/usr/bin/env python3
"""Unit tests for solution3.py"""

from io import StringIO
import pytest


# ============================================================
# TEST read_wordlist()
# ============================================================


def test_read_wordlist_basic():
    """read_wordlist() reads basic file"""
    from solution3 import read_wordlist

    file_obj = StringIO("apple\nbanana\ncherry\n")
    result = read_wordlist(file_obj)

    assert result == {"apple", "banana", "cherry"}


def test_read_wordlist_lowercase():
    """read_wordlist() converts uppercase to lowercase"""
    from solution3 import read_wordlist

    file_obj = StringIO("APPLE\nBanana\nChErRy")
    result = read_wordlist(file_obj)

    assert result == {"apple", "banana", "cherry"}


def test_read_wordlist_strips_whitespace():
    """read_wordlist() strips whitespace"""
    from solution3 import read_wordlist

    file_obj = StringIO("  apple  \n banana\n")
    result = read_wordlist(file_obj)

    assert result == {"apple", "banana"}


def test_read_wordlist_duplicates():
    """read_wordlist() removes duplicate words"""
    from solution3 import read_wordlist

    file_obj = StringIO("apple\nbanana\napple\n")
    result = read_wordlist(file_obj)

    assert result == {"apple", "banana"}
    assert len(result) == 2


def test_read_wordlist_empty():
    """read_wordlist() handles empty file"""
    from solution3 import read_wordlist

    file_obj = StringIO("")
    result = read_wordlist(file_obj)

    assert result == set()


def test_read_wordlist_none():
    """read_wordlist() handles None"""
    from solution3 import read_wordlist

    result = read_wordlist(None)

    assert result == set()


# ============================================================
# TEST filter_by_wordlist()
# ============================================================


def test_filter_by_wordlist_basic():
    """filter_by_wordlist() filters words in wordlist"""
    from solution3 import filter_by_wordlist

    rhymes = ["bake", "cake", "fake", "lake", "make"]
    wordlist = {"bake", "cake", "make"}

    result = filter_by_wordlist(rhymes, wordlist)

    assert result == ["bake", "cake", "make"]


def test_filter_by_wordlist_empty_wordlist():
    """filter_by_wordlist() returns all if wordlist empty"""
    from solution3 import filter_by_wordlist

    rhymes = ["bake", "cake", "fake"]
    wordlist = set()

    result = filter_by_wordlist(rhymes, wordlist)

    assert result == rhymes


def test_filter_by_wordlist_no_matches():
    """filter_by_wordlist() returns empty list if no match"""
    from solution3 import filter_by_wordlist

    rhymes = ["xake", "yake", "zake"]
    wordlist = {"bake", "cake"}

    result = filter_by_wordlist(rhymes, wordlist)

    assert result == []


def test_filter_by_wordlist_preserves_order():
    """filter_by_wordlist() preserves order"""
    from solution3 import filter_by_wordlist

    rhymes = ["cake", "bake", "make"]
    wordlist = {"bake", "cake", "make"}

    result = filter_by_wordlist(rhymes, wordlist)

    assert result == ["cake", "bake", "make"]


# ============================================================
# PARAMETRIZED TESTS
# ============================================================


@pytest.mark.parametrize(
    "word,expected",
    [
        ("cake", ("c", "ake")),
        ("dog", ("d", "og")),
        ("chair", ("ch", "air")),
        ("apple", ("", "apple")),
        ("", ("", "")),
        ("xyz", ("xyz", "")),
    ],
)
def test_stemmer_parametrized(word, expected):
    """Test stemmer with multiple inputs"""
    from solution3 import stemmer

    assert stemmer(word) == expected
