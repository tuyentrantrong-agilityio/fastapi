#!/usr/bin/env python3
"""Unit tests for solution1.py"""

import sys
import pytest
from io import StringIO


# ============================================================
# TEST get_prefixes()
# ============================================================


def test_get_prefixes_returns_list():
    """get_prefixes() should return a list"""
    from solution1 import get_prefixes

    result = get_prefixes()

    assert isinstance(result, list)


def test_get_prefixes_count():
    """get_prefixes() should return 57 prefixes"""
    from solution1 import get_prefixes

    result = get_prefixes()

    assert len(result) == 57


def test_get_prefixes_contains_single_consonants():
    """get_prefixes() contains single consonants"""
    from solution1 import get_prefixes

    result = get_prefixes()

    assert "b" in result
    assert "c" in result
    assert "z" in result


def test_get_prefixes_contains_clusters():
    """get_prefixes() contains consonant clusters"""
    from solution1 import get_prefixes

    result = get_prefixes()

    assert "ch" in result
    assert "str" in result
    assert "thr" in result


def test_get_prefixes_no_vowels():
    """get_prefixes() does not contain vowels"""
    from solution1 import get_prefixes

    result = get_prefixes()

    for vowel in "aeiou":
        assert vowel not in result


def test_get_prefixes_consistent():
    """get_prefixes() returns same result each call"""
    from solution1 import get_prefixes

    result1 = get_prefixes()
    result2 = get_prefixes()

    assert result1 == result2


# ============================================================
# TEST stemmer()
# ============================================================


def test_stemmer_empty_string():
    """stemmer() handles empty string"""
    from solution1 import stemmer

    assert stemmer("") == ("", "")


def test_stemmer_single_consonant():
    """stemmer() splits single consonant"""
    from solution1 import stemmer

    assert stemmer("cake") == ("c", "ake")
    assert stemmer("dog") == ("d", "og")
    assert stemmer("take") == ("t", "ake")


def test_stemmer_consonant_cluster():
    """stemmer() splits consonant cluster"""
    from solution1 import stemmer

    assert stemmer("chair") == ("ch", "air")
    assert stemmer("string") == ("str", "ing")
    assert stemmer("throw") == ("thr", "ow")


def test_stemmer_leading_vowel():
    """stemmer() handles word starting with vowel"""
    from solution1 import stemmer

    assert stemmer("apple") == ("", "apple")
    assert stemmer("egg") == ("", "egg")
    assert stemmer("ice") == ("", "ice")


def test_stemmer_no_vowels():
    """stemmer() handles word with no vowels"""
    from solution1 import stemmer

    assert stemmer("RDNZL") == ("rdnzl", "")
    assert stemmer("xyz") == ("xyz", "")


def test_stemmer_uppercase():
    """stemmer() converts uppercase to lowercase"""
    from solution1 import stemmer

    assert stemmer("CAKE") == ("c", "ake")
    assert stemmer("APPLE") == ("", "apple")


def test_stemmer_with_punctuation():
    """stemmer() removes punctuation"""
    from solution1 import stemmer

    assert stemmer("cake!!!") == ("c", "ake")
    assert stemmer("!!!cake") == ("c", "ake")


def test_stemmer_with_numbers():
    """stemmer() handles numbers"""
    from solution1 import stemmer

    assert stemmer("123") == ("123", "")


# ============================================================
# TEST create_rhymes()
# ============================================================


def test_create_rhymes_basic():
    """create_rhymes() creates rhymes list"""
    from solution1 import create_rhymes

    prefixes = ["b", "c", "f", "t"]
    result = create_rhymes("ake", "t", prefixes)

    # Exclude 't', 3 remaining
    assert len(result) == 3
    assert result == ["bake", "cake", "fake"]


def test_create_rhymes_sorted():
    """create_rhymes() returns sorted list"""
    from solution1 import create_rhymes

    prefixes = ["z", "a", "m", "b"]
    result = create_rhymes("ake", "", prefixes)

    assert result == sorted(result)


def test_create_rhymes_excludes_start():
    """create_rhymes() excludes original prefix"""
    from solution1 import create_rhymes

    prefixes = ["b", "c", "d"]
    result = create_rhymes("ake", "c", prefixes)

    assert "cake" not in result
    assert "bake" in result
    assert "dake" in result


def test_create_rhymes_with_cluster():
    """create_rhymes() works with consonant cluster"""
    from solution1 import create_rhymes

    prefixes = ["b", "ch", "th"]
    result = create_rhymes("air", "ch", prefixes)

    assert result == ["bair", "thair"]


def test_create_rhymes_empty_rest():
    """create_rhymes() handles empty rest"""
    from solution1 import create_rhymes

    prefixes = ["b", "c"]
    result = create_rhymes("", "x", prefixes)

    assert result == ["b", "c"]


# ============================================================
# TEST format_rhymes_output()
# ============================================================


def test_format_rhymes_output_single():
    """format_rhymes_output() formats single word"""
    from solution1 import format_rhymes_output

    result = format_rhymes_output(["bake"])

    assert result == "bake"


def test_format_rhymes_output_multiple():
    """format_rhymes_output() formats multiple words"""
    from solution1 import format_rhymes_output

    result = format_rhymes_output(["bake", "cake", "fake"])

    assert result == "bake\ncake\nfake"


def test_format_rhymes_output_empty():
    """format_rhymes_output() handles empty list"""
    from solution1 import format_rhymes_output

    result = format_rhymes_output([])

    assert result == ""


# ============================================================
# TEST format_no_rhyme_message()
# ============================================================


def test_format_no_rhyme_message():
    """format_no_rhyme_message() creates correct message"""
    from solution1 import format_no_rhyme_message

    result = format_no_rhyme_message("xyz")

    assert result == "Cannot rhyme with xyz"


def test_format_no_rhyme_message_preserves_case():
    """format_no_rhyme_message() preserves case"""
    from solution1 import format_no_rhyme_message

    assert format_no_rhyme_message("XYZ") == "Cannot rhyme with XYZ"
    assert format_no_rhyme_message("xyz") == "Cannot rhyme with xyz"


# ============================================================
# TEST get_args()
# ============================================================


def test_get_args_with_word():
    """get_args() parse word argument"""
    from solution1 import get_args

    sys.argv = ["solution1.py", "cake"]
    args = get_args()

    assert args.text == "cake"


def test_get_args_required():
    """get_args() requires word argument"""
    from solution1 import get_args

    sys.argv = ["solution1.py"]

    with pytest.raises(SystemExit):
        get_args()


# ============================================================
# TEST main() - Integration với các hàm
# ============================================================


def test_main_with_cake(capsys, monkeypatch):
    """main() prints rhymes for 'cake'"""
    from solution1 import main

    monkeypatch.setattr("sys.argv", ["solution1.py", "cake"])
    main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")

    assert len(lines) == 56  # 57 - 1 (exclude 'c')
    assert lines[0] == "bake"
    assert "cake" not in lines


def test_main_with_apple(capsys, monkeypatch):
    """main() prints rhymes for 'apple'"""
    from solution1 import main

    monkeypatch.setattr("sys.argv", ["solution1.py", "apple"])
    main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")

    assert len(lines) == 57  # No prefix excluded
    assert "bapple" in lines


def test_main_with_no_vowels(capsys, monkeypatch):
    """main() prints error for word with no vowels"""
    from solution1 import main

    monkeypatch.setattr("sys.argv", ["solution1.py", "XYZ"])
    main()

    captured = capsys.readouterr()

    assert captured.out.strip() == "Cannot rhyme with XYZ"
