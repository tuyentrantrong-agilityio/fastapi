#!/usr/bin/env python3
"""Unit tests for solution2.py"""

import sys
import pytest


# ============================================================
# TEST get_prefixes()
# ============================================================


def test_get_prefixes_returns_list():
    """get_prefixes() should return a list"""
    from solution2 import get_prefixes

    result = get_prefixes()

    assert isinstance(result, list)


def test_get_prefixes_count():
    """get_prefixes() should return 57 prefixes"""
    from solution2 import get_prefixes

    result = get_prefixes()

    assert len(result) == 57


def test_get_prefixes_contains_single_consonants():
    """get_prefixes() contains single consonants"""
    from solution2 import get_prefixes

    result = get_prefixes()

    assert "b" in result
    assert "c" in result
    assert "z" in result


def test_get_prefixes_contains_clusters():
    """get_prefixes() contains consonant clusters"""
    from solution2 import get_prefixes

    result = get_prefixes()

    assert "ch" in result
    assert "str" in result
    assert "thr" in result


# ============================================================
# TEST stemmer() - ITERATIVE APPROACH
# ============================================================


def test_stemmer_empty_string():
    """stemmer() handles empty string"""
    from solution2 import stemmer

    assert stemmer("") == ("", "")


def test_stemmer_single_consonant():
    """stemmer() splits single consonant"""
    from solution2 import stemmer

    assert stemmer("cake") == ("c", "ake")
    assert stemmer("dog") == ("d", "og")


def test_stemmer_consonant_cluster():
    """stemmer() splits consonant cluster"""
    from solution2 import stemmer

    assert stemmer("chair") == ("ch", "air")
    assert stemmer("string") == ("str", "ing")


def test_stemmer_leading_vowel():
    """stemmer() handles word starting with vowel"""
    from solution2 import stemmer

    assert stemmer("apple") == ("", "apple")


def test_stemmer_no_vowels():
    """stemmer() handles word with no vowels"""
    from solution2 import stemmer

    assert stemmer("xyz") == ("xyz", "")


def test_stemmer_with_punctuation():
    """stemmer() removes punctuation"""
    from solution2 import stemmer

    assert stemmer("cake!!!") == ("c", "ake")


# ============================================================
# TEST create_rhymes()
# ============================================================


def test_create_rhymes_basic():
    """create_rhymes() creates rhymes list"""
    from solution2 import create_rhymes

    prefixes = ["b", "c", "f", "t"]
    result = create_rhymes("ake", "t", prefixes)

    # Exclude 't', 3 remaining
    assert len(result) == 3
    assert result == ["bake", "cake", "fake"]


def test_create_rhymes_sorted():
    """create_rhymes() returns sorted list"""
    from solution2 import create_rhymes

    prefixes = ["z", "a", "m", "b"]
    result = create_rhymes("ake", "", prefixes)

    assert result == sorted(result)


def test_create_rhymes_excludes_start():
    """create_rhymes() excludes original prefix"""
    from solution2 import create_rhymes

    prefixes = ["b", "c", "d"]
    result = create_rhymes("ake", "c", prefixes)

    assert "cake" not in result
    assert "bake" in result


# ============================================================
# TEST format_rhymes_output()
# ============================================================


def test_format_rhymes_output_single():
    """format_rhymes_output() formats single word"""
    from solution2 import format_rhymes_output

    result = format_rhymes_output(["bake"])

    assert result == "bake"


def test_format_rhymes_output_multiple():
    """format_rhymes_output() formats multiple words"""
    from solution2 import format_rhymes_output

    result = format_rhymes_output(["bake", "cake", "fake"])

    assert result == "bake\ncake\nfake"


# ============================================================
# TEST format_no_rhyme_message()
# ============================================================


def test_format_no_rhyme_message():
    """format_no_rhyme_message() creates correct message"""
    from solution2 import format_no_rhyme_message

    result = format_no_rhyme_message("xyz")

    assert result == "Cannot rhyme with xyz"


# ============================================================
# TEST get_args()
# ============================================================


def test_get_args_with_word():
    """get_args() parse word argument"""
    from solution2 import get_args

    sys.argv = ["solution2.py", "cake"]
    args = get_args()

    assert args.text == "cake"


# ============================================================
# TEST main()
# ============================================================


def test_main_with_cake(capsys, monkeypatch):
    """main() prints rhymes for 'cake'"""
    from solution2 import main

    monkeypatch.setattr("sys.argv", ["solution2.py", "cake"])
    main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")

    assert len(lines) == 56  # 57 - 1 (exclude 'c')
    assert lines[0] == "bake"
    assert "cake" not in lines


def test_main_with_apple(capsys, monkeypatch):
    """main() prints rhymes for 'apple'"""
    from solution2 import main

    monkeypatch.setattr("sys.argv", ["solution2.py", "apple"])
    main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")

    assert len(lines) == 57
    assert "bapple" in lines


def test_main_with_no_vowels(capsys, monkeypatch):
    """main() prints error for word with no vowels"""
    from solution2 import main

    monkeypatch.setattr("sys.argv", ["solution2.py", "XYZ"])
    main()

    captured = capsys.readouterr()

    assert captured.out.strip() == "Cannot rhyme with XYZ"
