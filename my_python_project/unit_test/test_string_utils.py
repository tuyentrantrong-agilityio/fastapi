import unittest


class StringUtils:
    """Simple string utilities for testing"""

    def reverse_string(self, s):
        return s[::-1]

    def is_palindrome(self, s):
        clean = s.lower().replace(" ", "")
        return clean == clean[::-1]

    def count_vowels(self, s):
        vowels = "aeiouAEIOU"
        return sum(1 for char in s if char in vowels)


class TestStringUtils(unittest.TestCase):
    def setUp(self):
        self.utils = StringUtils()

    def test_reverse_string(self):
        self.assertEqual(self.utils.reverse_string("hello"), "olleh")
        self.assertEqual(self.utils.reverse_string(""), "")

    def test_is_palindrome(self):
        self.assertTrue(self.utils.is_palindrome("racecar"))
        self.assertFalse(self.utils.is_palindrome("hello"))

    def test_count_vowels(self):
        self.assertEqual(self.utils.count_vowels("hello"), 2)
        self.assertEqual(self.utils.count_vowels("aeiou"), 5)


if __name__ == "__main__":
    unittest.main()
