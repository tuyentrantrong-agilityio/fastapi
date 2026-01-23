#!/usr/bin/env python3
"""Pure Unit Tests - Testing only non-main functions
Test get_args() function of hello07 and hello08 only"""

import unittest
from unittest.mock import patch
import argparse

import hello07_get_args as hello07
import hello08_formatted as hello08


class TestHello07GetArgs(unittest.TestCase):
    """Unit tests for hello07_get_args.get_args() - default 'World'"""

    def test_returns_namespace_object(self):
        """hello07.get_args() returns argparse.Namespace"""
        with patch("sys.argv", ["hello07"]):
            result = hello07.get_args()
            self.assertIsInstance(result, argparse.Namespace)

    def test_default_world(self):
        """hello07.get_args() default is 'World'"""
        with patch("sys.argv", ["hello07"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "World")

    def test_short_flag(self):
        """hello07.get_args() accepts -n flag"""
        with patch("sys.argv", ["hello07", "-n", "Alice"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "Alice")

    def test_long_flag(self):
        """hello07.get_args() accepts --name flag"""
        with patch("sys.argv", ["hello07", "--name", "Bob"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "Bob")

    def test_special_characters(self):
        """hello07.get_args() handles special characters"""
        with patch("sys.argv", ["hello07", "-n", "@#$%"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "@#$%")

    def test_unicode_name(self):
        """hello07.get_args() handles Unicode characters"""
        with patch("sys.argv", ["hello07", "-n", "你好"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "你好")

    def test_empty_string(self):
        """hello07.get_args() handles empty string"""
        with patch("sys.argv", ["hello07", "-n", ""]):
            result = hello07.get_args()
            self.assertEqual(result.name, "")

    def test_name_with_spaces(self):
        """hello07.get_args() handles names with spaces"""
        with patch("sys.argv", ["hello07", "-n", "John Doe"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "John Doe")


class TestHello08GetArgs(unittest.TestCase):
    """Unit tests for hello08_formatted.get_args() - default 'Tuyen'"""

    def test_returns_namespace_object(self):
        """hello08.get_args() returns argparse.Namespace"""
        with patch("sys.argv", ["hello08"]):
            result = hello08.get_args()
            self.assertIsInstance(result, argparse.Namespace)

    def test_default_name_is_tuyen(self):
        """hello08.get_args() default is 'Tuyen' (different from hello06/07)"""
        with patch("sys.argv", ["hello08"]):
            result = hello08.get_args()
            self.assertEqual(result.name, "Tuyen")

    def test_short_flag(self):
        """hello08.get_args() accepts -n flag"""
        with patch("sys.argv", ["hello08", "-n", "Grace"]):
            result = hello08.get_args()
            self.assertEqual(result.name, "Grace")

    def test_long_flag(self):
        """hello08.get_args() accepts --name flag"""
        with patch("sys.argv", ["hello08", "--name", "Henry"]):
            result = hello08.get_args()
            self.assertEqual(result.name, "Henry")

    def test_long_name(self):
        """hello08.get_args() handles very long names"""
        long_name = "A" * 1000
        with patch("sys.argv", ["hello08", "-n", long_name]):
            result = hello08.get_args()
            self.assertEqual(result.name, long_name)


class TestGetArgsComparison(unittest.TestCase):
    """Compare get_args() between hello07 and hello08"""

    def test_different_defaults(self):
        """hello07 and hello08 have different default values"""
        with patch("sys.argv", ["hello07"]):
            result07 = hello07.get_args()

        with patch("sys.argv", ["hello08"]):
            result08 = hello08.get_args()

        self.assertEqual(result07.name, "World")
        self.assertEqual(result08.name, "Tuyen")
        self.assertNotEqual(result07.name, result08.name)


class TestGetArgsBoundaryConditions(unittest.TestCase):
    """Test boundary conditions for get_args()"""

    def test_single_character(self):
        """get_args() handles single character"""
        with patch("sys.argv", ["hello07", "-n", "A"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "A")

    def test_numeric_string(self):
        """get_args() handles numeric string"""
        with patch("sys.argv", ["hello08", "-n", "12345"]):
            result = hello08.get_args()
            self.assertEqual(result.name, "12345")

    def test_special_characters(self):
        """get_args() handles special characters"""
        with patch("sys.argv", ["hello07", "-n", "@#$%^&*()"]):
            result = hello07.get_args()
            self.assertEqual(result.name, "@#$%^&*()")


if __name__ == "__main__":
    unittest.main(verbosity=2)
