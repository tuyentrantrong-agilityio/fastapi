#!/usr/bin/env python3
"""tests for hello.py using unittest"""

import unittest
import os
from subprocess import getstatusoutput, getoutput


class TestHello(unittest.TestCase):
    """Test cases for hello07_get_args.py (want to test file, to fix path)"""

    def setUp(self):
        """Set up test fixtures"""
        self.prg = "hello07_get_args.py"

    # --------------------------------------------------
    def test_exists(self):
        """File exists"""
        self.assertTrue(os.path.isfile(self.prg))

    # --------------------------------------------------
    def test_runnable(self):
        """Runs using python3"""
        out = getoutput(f"python3 {self.prg}")
        self.assertEqual(out.strip(), "Hello, World!")

    # --------------------------------------------------
    def test_executable(self):
        """Says 'Hello, World!' by default"""
        out = getoutput(f"python3 {self.prg}")
        self.assertEqual(out.strip(), "Hello, World!")

    # --------------------------------------------------
    def test_usage(self):
        """Usage help displays correctly"""
        for flag in ["-h", "--help"]:
            with self.subTest(flag=flag):
                rv, out = getstatusoutput(f"python3 {self.prg} {flag}")
                self.assertEqual(rv, 0)
                self.assertTrue(out.lower().startswith("usage"))

    # --------------------------------------------------
    def test_input(self):
        """Test with input arguments"""
        for val in ["Universe", "Multiverse"]:
            for option in ["-n", "--name"]:
                with self.subTest(val=val, option=option):
                    rv, out = getstatusoutput(f"python3 {self.prg} {option} {val}")
                    self.assertEqual(rv, 0)
                    self.assertEqual(out.strip(), f"Hello, {val}!")


if __name__ == "__main__":
    unittest.main()
