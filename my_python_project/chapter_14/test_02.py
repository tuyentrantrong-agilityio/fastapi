import unittest
from subprocess import getoutput
import os

prg = "solution3.py"  # Run solution3.py with python3


class TestSolution3(unittest.TestCase):
    """Test cases for solution3.py"""

    def test_exists(self):
        """Test that solution3.py exists"""
        self.assertTrue(os.path.isfile(prg))

    def test_usage(self):
        """Test usage with different flags"""
        for flag in ["", "-h", "--help"]:
            out = getoutput(f"python3 {prg} {flag}")
            self.assertTrue(out.lower().startswith("usage"))

    def test_dog(self):
        """Test with custom word 'dog'"""
        word = "dog"
        out = getoutput(f"python3 {prg} {word}").splitlines()
        self.assertEqual(len(out), 56)
        self.assertEqual(out[0], "blog")
        self.assertEqual(out[-1], "zog")
        self.assertNotIn(word, out)

    def test_apple(self):
        """Test with custom word 'apple'"""
        word = "apple"
        out = getoutput(f"python3 {prg} {word}").splitlines()
        self.assertEqual(len(out), 57)
        self.assertEqual(out[0], "bapple")
        self.assertEqual(out[-1], "zapple")

    def test_no_vowels(self):
        """Test word with no vowels"""
        out = getoutput(f"python3 {prg} ZYX")
        self.assertEqual(out, "Cannot rhyme with ZYX")

    def test_uppercase(self):
        """Test uppercase and lowercase produce same output"""
        out1 = getoutput(f"python3 {prg} APPLE").splitlines()
        out2 = getoutput(f"python3 {prg} apple").splitlines()
        self.assertEqual(out1, out2)


if __name__ == "__main__":
    unittest.main()
