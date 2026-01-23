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





if __name__ == "__main__":
    unittest.main()
