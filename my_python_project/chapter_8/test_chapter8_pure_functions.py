#!/usr/bin/env python3
"""Unit Tests for chapter_8 - Test pure functions extracted from examples"""

import unittest
import sys
from pathlib import Path
import importlib.util
import re
from functools import partial

# Add current directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent))

import example1_iterate_chars as ex1
import example2_str_replace as ex2
import example4_list_comprehension as ex4
import example5_list_comp_function as ex5
import example5_no_closure as ex5_no
import example6_map_lambda as ex6
import example7_map_function as ex7
import example8_regex as ex8

# Load example3_ module using spec due to special name with dot
spec = importlib.util.spec_from_file_location(
    "example3_str_translate", Path(__file__).parent / "example3_.str_translate.py"
)
ex3 = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(ex3)


class TestReplaceVowelsIterate(unittest.TestCase):
    """Unit tests for example1_iterate_chars.replace_vowels_iterate()"""

    def test_replace_single_lowercase_vowel(self):
        """Replace single lowercase vowel"""
        result = ex1.replace_vowels_iterate("apple", "e")
        self.assertEqual(result, "epple")

    def test_replace_single_uppercase_vowel(self):
        """Replace single uppercase vowel"""
        result = ex1.replace_vowels_iterate("APPLE", "E")
        self.assertEqual(result, "EPPLE")

    def test_replace_mixed_case_vowels(self):
        """Replace mixed case vowels"""
        result = ex1.replace_vowels_iterate("Hello", "i")
        self.assertEqual(result, "Hilli")

    def test_replace_all_vowels(self):
        """Replace all vowels with same vowel"""
        result = ex1.replace_vowels_iterate("aeiouAEIOU", "a")
        self.assertEqual(result, "aaaaaAAAAA")

    def test_no_vowels_in_text(self):
        """Text without vowels remains unchanged"""
        result = ex1.replace_vowels_iterate("bcdfg", "a")
        self.assertEqual(result, "bcdfg")

    def test_consonants_unchanged(self):
        """Consonants remain unchanged"""
        result = ex1.replace_vowels_iterate("hello", "a")
        self.assertEqual(result, "halla")

    def test_empty_string(self):
        """Empty string returns empty"""
        result = ex1.replace_vowels_iterate("", "a")
        self.assertEqual(result, "")

    def test_single_vowel(self):
        """Single vowel replacement"""
        result = ex1.replace_vowels_iterate("a", "e")
        self.assertEqual(result, "e")

    def test_preserve_case_lowercase(self):
        """Preserve case - lowercase vowel stays lowercase"""
        result = ex1.replace_vowels_iterate("apple", "o")
        self.assertEqual(result, "opplo")

    def test_preserve_case_uppercase(self):
        """Preserve case - uppercase vowel becomes uppercase replacement"""
        result = ex1.replace_vowels_iterate("APPLE", "o")
        self.assertEqual(result, "OPPLO")

    def test_with_numbers_and_special_chars(self):
        """Handle numbers and special characters"""
        result = ex1.replace_vowels_iterate("a1b2@e3", "i")
        self.assertEqual(result, "i1b2@i3")

    def test_space_characters(self):
        """Spaces are preserved"""
        result = ex1.replace_vowels_iterate("apple banana", "e")
        self.assertEqual(result, "epple benene")

    def test_multiple_same_vowels(self):
        """Multiple same vowels replaced"""
        result = ex1.replace_vowels_iterate("aaa", "e")
        self.assertEqual(result, "eee")


class TestReplaceVowelsStrMethod(unittest.TestCase):
    """Unit tests for example2_str_replace.replace_vowels_str_method()"""

    def test_replace_lowercase_vowel(self):
        """Replace lowercase vowel"""
        result = ex2.replace_vowels_str_method("apple", "e")
        self.assertEqual(result, "epple")

    def test_replace_uppercase_vowel(self):
        """Replace uppercase vowel"""
        result = ex2.replace_vowels_str_method("APPLE", "e")
        self.assertEqual(result, "EPPLE")

    def test_replace_mixed_case(self):
        """Replace mixed case vowels"""
        result = ex2.replace_vowels_str_method("Hello World", "i")
        self.assertEqual(result, "Hilli Wirld")

    def test_all_vowels_to_a(self):
        """Replace all vowels with 'a'"""
        result = ex2.replace_vowels_str_method("aeiouAEIOU", "a")
        self.assertEqual(result, "aaaaaAAAAA")

    def test_no_vowels(self):
        """Text without vowels unchanged"""
        result = ex2.replace_vowels_str_method("bcdfg", "e")
        self.assertEqual(result, "bcdfg")

    def test_empty_string(self):
        """Empty string returns empty"""
        result = ex2.replace_vowels_str_method("", "a")
        self.assertEqual(result, "")

    def test_single_character_vowel(self):
        """Single vowel character"""
        result = ex2.replace_vowels_str_method("a", "o")
        self.assertEqual(result, "o")

    def test_numbers_preserved(self):
        """Numbers are preserved"""
        result = ex2.replace_vowels_str_method("a1b2e3", "i")
        self.assertEqual(result, "i1b2i3")

    def test_special_chars_preserved(self):
        """Special characters preserved"""
        result = ex2.replace_vowels_str_method("@apple#", "e")
        self.assertEqual(result, "@epple#")

    def test_space_preserved(self):
        """Spaces preserved"""
        result = ex2.replace_vowels_str_method("hello world", "a")
        self.assertEqual(result, "halla warld")


class TestReplaceVowelsTranslate(unittest.TestCase):
    """Unit tests for example3_str_translate.replace_vowels_translate()"""

    def test_replace_lowercase_vowel(self):
        """Replace lowercase vowel"""
        result = ex3.replace_vowels_translate("apple", "e")
        self.assertEqual(result, "epple")

    def test_replace_uppercase_vowel(self):
        """Replace uppercase vowel"""
        result = ex3.replace_vowels_translate("APPLE", "e")
        self.assertEqual(result, "EPPLE")

    def test_replace_mixed_case(self):
        """Replace mixed case vowels"""
        result = ex3.replace_vowels_translate("Hello", "i")
        self.assertEqual(result, "Hilli")

    def test_all_vowels(self):
        """Replace all vowels"""
        result = ex3.replace_vowels_translate("aeiouAEIOU", "a")
        self.assertEqual(result, "aaaaaAAAAA")

    def test_no_vowels(self):
        """Text without vowels unchanged"""
        result = ex3.replace_vowels_translate("bcdfg", "e")
        self.assertEqual(result, "bcdfg")

    def test_empty_string(self):
        """Empty string returns empty"""
        result = ex3.replace_vowels_translate("", "a")
        self.assertEqual(result, "")

    def test_single_vowel(self):
        """Single vowel replacement"""
        result = ex3.replace_vowels_translate("a", "o")
        self.assertEqual(result, "o")

    def test_numbers_and_special_chars(self):
        """Numbers and special characters preserved"""
        result = ex3.replace_vowels_translate("a1@b2#e3", "i")
        self.assertEqual(result, "i1@b2#i3")

    def test_spaces_preserved(self):
        """Spaces preserved"""
        result = ex3.replace_vowels_translate("apple banana", "e")
        self.assertEqual(result, "epple benene")


class TestCompareMethodsConsistency(unittest.TestCase):
    """Test that all three methods produce same results"""

    def test_all_methods_same_result_simple(self):
        """All methods produce same result for simple text"""
        text = "hello"
        vowel = "a"

        result1 = ex1.replace_vowels_iterate(text, vowel)
        result2 = ex2.replace_vowels_str_method(text, vowel)
        result3 = ex3.replace_vowels_translate(text, vowel)
        result4 = ex4.replace_vowels_listcomp(text, vowel)
        result5 = ex5.replace_vowels_closure(text, vowel)
        result5_no = ex5_no.replace_vowels_helper(text, vowel)
        result6 = ex6.replace_vowels_map_lambda(text, vowel)
        result7 = ex7.replace_vowels_map_partial(text, vowel)
        result8 = ex8.replace_vowels_regex(text, vowel)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result3, result4)
        self.assertEqual(result4, result5)
        self.assertEqual(result5, result5_no)
        self.assertEqual(result5_no, result6)
        self.assertEqual(result6, result7)
        self.assertEqual(result7, result8)

    def test_all_methods_same_result_mixed_case(self):
        """All methods produce same result for mixed case"""
        text = "Apple BANANA cherry"
        vowel = "i"

        result1 = ex1.replace_vowels_iterate(text, vowel)
        result2 = ex2.replace_vowels_str_method(text, vowel)
        result3 = ex3.replace_vowels_translate(text, vowel)
        result4 = ex4.replace_vowels_listcomp(text, vowel)
        result5 = ex5.replace_vowels_closure(text, vowel)
        result5_no = ex5_no.replace_vowels_helper(text, vowel)
        result6 = ex6.replace_vowels_map_lambda(text, vowel)
        result7 = ex7.replace_vowels_map_partial(text, vowel)
        result8 = ex8.replace_vowels_regex(text, vowel)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result3, result4)
        self.assertEqual(result4, result5)
        self.assertEqual(result5, result5_no)
        self.assertEqual(result5_no, result6)
        self.assertEqual(result6, result7)
        self.assertEqual(result7, result8)

    def test_all_methods_same_result_all_vowels(self):
        """All methods produce same result with all vowels"""
        text = "aeiouAEIOU"
        vowel = "a"

        result1 = ex1.replace_vowels_iterate(text, vowel)
        result2 = ex2.replace_vowels_str_method(text, vowel)
        result3 = ex3.replace_vowels_translate(text, vowel)
        result4 = ex4.replace_vowels_listcomp(text, vowel)
        result5 = ex5.replace_vowels_closure(text, vowel)
        result5_no = ex5_no.replace_vowels_helper(text, vowel)
        result6 = ex6.replace_vowels_map_lambda(text, vowel)
        result7 = ex7.replace_vowels_map_partial(text, vowel)
        result8 = ex8.replace_vowels_regex(text, vowel)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result3, result4)
        self.assertEqual(result4, result5)
        self.assertEqual(result5, result5_no)
        self.assertEqual(result5_no, result6)
        self.assertEqual(result6, result7)
        self.assertEqual(result7, result8)

    def test_all_methods_same_result_no_vowels(self):
        """All methods produce same result for text without vowels"""
        text = "bcdfg xyz"
        vowel = "a"

        result1 = ex1.replace_vowels_iterate(text, vowel)
        result2 = ex2.replace_vowels_str_method(text, vowel)
        result3 = ex3.replace_vowels_translate(text, vowel)
        result4 = ex4.replace_vowels_listcomp(text, vowel)
        result5 = ex5.replace_vowels_closure(text, vowel)
        result5_no = ex5_no.replace_vowels_helper(text, vowel)
        result6 = ex6.replace_vowels_map_lambda(text, vowel)
        result7 = ex7.replace_vowels_map_partial(text, vowel)
        result8 = ex8.replace_vowels_regex(text, vowel)

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result3, result4)
        self.assertEqual(result4, result5)
        self.assertEqual(result5, result5_no)
        self.assertEqual(result5_no, result6)
        self.assertEqual(result6, result7)
        self.assertEqual(result7, result8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
