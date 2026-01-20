#!/usr/bin/env python3
"""Unit tests for examples (convert from pytest to unittest)"""

import re
import unittest
import os
from subprocess import getstatusoutput, getoutput


class TestExamples(unittest.TestCase):
    """Test cases converted from pytest to unittest"""

    def setUp(self):
        """Set up test fixtures"""
        self.prg = "example1_iterate_chars.py"  # Change this to test different files
        self.fox = "../inputs/fox.txt"

    # --------------------------------------------------
    def test_exists(self):
        """File exists"""
        self.assertTrue(os.path.isfile(self.prg))

    # --------------------------------------------------
    def test_usage(self):
        """Test usage help"""
        for flag in ["-h", "--help"]:
            with self.subTest(flag=flag):
                rv, out = getstatusoutput(f"python3 {self.prg} {flag}")
                self.assertEqual(rv, 0)
                self.assertIsNotNone(re.match("usage", out, re.IGNORECASE))

    # --------------------------------------------------
    def test_bad_vowel(self):
        """Should fail on a bad vowel"""
        rv, out = getstatusoutput(f"python3 {self.prg} -v x foo")
        self.assertNotEqual(rv, 0)
        self.assertIsNotNone(re.match("usage", out, re.IGNORECASE))

    # --------------------------------------------------
    def test_command_line(self):
        """Test command line: foo -> faa"""
        out = getoutput(f"python3 {self.prg} foo")
        self.assertEqual(out.strip(), "faa")

    # --------------------------------------------------
    def test_command_line_with_vowel(self):
        """Test command line with vowel: foo -> fii"""
        out = getoutput(f"python3 {self.prg} -v i foo")
        self.assertEqual(out.strip(), "fii")

    # --------------------------------------------------
    def test_command_line_with_vowel_preserve_case(self):
        """Test preserve case with uppercase vowel"""
        out = getoutput(f'python3 {self.prg} "APPLES AND BANANAS" --vowel i')
        self.assertEqual(out.strip(), "IPPLIS IND BININIS")

    # --------------------------------------------------
    def test_file(self):
        """Test with file input"""
        out = getoutput(f"python3 {self.prg} {self.fox}")
        self.assertEqual(out.strip(), "Tha qaack brawn fax jamps avar tha lazy dag.")

    # --------------------------------------------------
    def test_file_with_vowel(self):
        """Test file with different vowel"""
        out = getoutput(f"python3 {self.prg} --vowel o {self.fox}")
        self.assertEqual(out.strip(), "Tho qoock brown fox jomps ovor tho lozy dog.")


if __name__ == "__main__":
    unittest.main()
