"""Traditional unittest for example1_iterate_chars.py"""

import unittest
from example1_iterate_chars import replace_vowels_iterate


class TestReplaceVowelsIterate(unittest.TestCase):
    """Test cases for replace_vowels_iterate function"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_text = "hello"
        self.test_vowel = "a"
        self.expected_result = "halla"

    def tearDown(self):
        """Clean up after each test method"""
        self.test_text = None
        self.test_vowel = None
        self.expected_result = None

    def test_replace_with_vowel_a(self):
        """Test replacing vowels with 'a'"""
        result = replace_vowels_iterate("hello", "a")
        self.assertEqual(result, "halla")

    def test_replace_with_vowel_e(self):
        """Test replacing vowels with 'e'"""
        result = replace_vowels_iterate("hello", "e")
        self.assertEqual(result, "helle")

    def test_replace_with_vowel_o(self):
        """Test replacing vowels with 'o'"""
        result = replace_vowels_iterate("banana", "o")
        self.assertEqual(result, "bonono")

    def test_uppercase_vowels(self):
        """Test replacing uppercase vowels"""
        result = replace_vowels_iterate("HELLO", "a")
        self.assertEqual(result, "HALLA")

    def test_mixed_case_vowels(self):
        """Test replacing both lowercase and uppercase vowels"""
        result = replace_vowels_iterate("Hello World", "e")
        self.assertEqual(result, "Helle Werld")

    def test_consonants_unchanged(self):
        """Test that consonants remain unchanged"""
        result = replace_vowels_iterate("xyz", "a")
        self.assertEqual(result, "xyz")

    def test_empty_string(self):
        """Test with empty string"""
        result = replace_vowels_iterate("", "a")
        self.assertEqual(result, "")

    def test_no_vowels(self):
        """Test string with no vowels"""
        result = replace_vowels_iterate("bcdfg", "a")
        self.assertEqual(result, "bcdfg")

    def test_all_vowels(self):
        """Test string with all vowels"""
        result = replace_vowels_iterate("aeiou", "o")
        self.assertEqual(result, "ooooo")

    def test_all_uppercase_vowels(self):
        """Test string with all uppercase vowels"""
        result = replace_vowels_iterate("AEIOU", "e")
        self.assertEqual(result, "EEEEE")

    def test_with_spaces_and_punctuation(self):
        """Test string with spaces and punctuation"""
        result = replace_vowels_iterate("Hello, World!", "a")
        self.assertEqual(result, "Halla, Warld!")

    def test_single_vowel(self):
        """Test single vowel character"""
        result = replace_vowels_iterate("a", "e")
        self.assertEqual(result, "e")

    def test_single_uppercase_vowel(self):
        """Test single uppercase vowel character"""
        result = replace_vowels_iterate("A", "e")
        self.assertEqual(result, "E")

    def test_numbers_in_text(self):
        """Test string with numbers"""
        result = replace_vowels_iterate("abc123def", "o")
        self.assertEqual(result, "obc123dof")


if __name__ == "__main__":
    unittest.main()
