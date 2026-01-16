"""
Comprehensive unittest demo: from basic to advanced
Demonstrates: TestCase, assert, setUp, subTest, skip, expectedFailure,
TestSuite, TestLoader, load_tests, and unittest.main
"""

import unittest
from unittest import TestCase, TestSuite, TestLoader, skip, expectedFailure


# ===========================
# Helper functions for testing
# ===========================


def add(a, b):
    """Simple addition function"""
    return a + b


def subtract(a, b):
    """Simple subtraction function"""
    return a - b


def multiply(a, b):
    """Simple multiplication function"""
    return a * b


def divide(a, b):
    """Divide function with zero check"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def is_even(n):
    """Check if number is even"""
    return n % 2 == 0


class Calculator:
    """Simple calculator class"""

    def __init__(self, initial_value=0):
        self.value = initial_value

    def add(self, x):
        self.value += x

    def clear(self):
        self.value = 0


# ===========================
# Test Cases
# ===========================


class TestBasicAssertions(TestCase):
    """Demonstrate basic assertion methods"""

    def test_assertEqual(self):
        """Test assertEqual: checks if two values are equal"""
        result = add(2, 3)
        self.assertEqual(result, 5)

    def test_assertNotEqual(self):
        """Test assertNotEqual: checks if two values are different"""
        result = subtract(10, 5)
        self.assertNotEqual(result, 10)

    def test_assertTrue(self):
        """Test assertTrue: checks if condition is True"""
        result = is_even(4)
        self.assertTrue(result)

    def test_assertFalse(self):
        """Test assertFalse: checks if condition is False"""
        result = is_even(5)
        self.assertFalse(result)

    def test_assertIn(self):
        """Test assertIn: checks if value is in container"""
        items = [1, 2, 3, 4, 5]
        self.assertIn(3, items)

    def test_assertNotIn(self):
        """Test assertNotIn: checks if value is NOT in container"""
        items = [1, 2, 3, 4, 5]
        self.assertNotIn(10, items)

    def test_assertIsNone(self):
        """Test assertIsNone: checks if value is None"""
        result = None
        self.assertIsNone(result)

    def test_assertIsNotNone(self):
        """Test assertIsNotNone: checks if value is NOT None"""
        result = "something"
        self.assertIsNotNone(result)

    def test_assertGreater(self):
        """Test assertGreater: checks if first > second"""
        self.assertGreater(10, 5)

    def test_assertLess(self):
        """Test assertLess: checks if first < second"""
        self.assertLess(3, 8)


class TestSetUpTearDown(TestCase):
    """Demonstrate setUp and tearDown methods"""

    def setUp(self):
        """Called before each test - initialize test fixtures"""
        self.calculator = Calculator(10)
        print("  [setUp] Calculator initialized with value 10")

    def tearDown(self):
        """Called after each test - cleanup resources"""
        self.calculator.clear()
        print("  [tearDown] Calculator cleared")

    def test_initial_value(self):
        """Test initial value after setUp"""
        self.assertEqual(self.calculator.value, 10)

    def test_add_operation(self):
        """Test add operation"""
        self.calculator.add(5)
        self.assertEqual(self.calculator.value, 15)

    def test_multiple_adds(self):
        """Test multiple add operations"""
        self.calculator.add(3)
        self.calculator.add(7)
        self.assertEqual(self.calculator.value, 20)


class TestSubTest(TestCase):
    """Demonstrate subTest for parameterized testing"""

    def test_add_multiple_cases(self):
        """Test add function with multiple test cases using subTest"""
        test_cases = [
            (2, 3, 5),
            (0, 0, 0),
            (-1, 1, 0),
            (100, 50, 150),
        ]

        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                result = add(a, b)
                self.assertEqual(result, expected)

    def test_multiply_multiple_cases(self):
        """Test multiply function with subTest"""
        test_cases = [
            (2, 3, 6),
            (0, 5, 0),
            (-2, 3, -6),
            (1, 1, 1),
        ]

        for a, b, expected in test_cases:
            with self.subTest(operation=f"{a} * {b}"):
                result = multiply(a, b)
                self.assertEqual(result, expected)


class TestExceptions(TestCase):
    """Test exception handling"""

    def test_divide_by_zero_raises_exception(self):
        """Test that divide by zero raises ValueError"""
        with self.assertRaises(ValueError):
            divide(10, 0)

    def test_divide_raises_with_message(self):
        """Test exception message"""
        with self.assertRaisesRegex(ValueError, "Cannot divide"):
            divide(5, 0)

    def test_divide_valid(self):
        """Test valid division"""
        result = divide(10, 2)
        self.assertEqual(result, 5)


class TestSkip(TestCase):
    """Demonstrate skip and skipIf decorators"""

    @skip("Skipping this test - under development")
    def test_skipped_test(self):
        """This test will be skipped"""
        self.assertEqual(1, 2)

    def test_conditional_skip(self):
        """Use skipIf inside test"""
        skip_condition = True
        if skip_condition:
            self.skipTest("Skipped conditionally")
        self.assertEqual(1, 1)


class TestExpectedFailure(TestCase):
    """Demonstrate expectedFailure decorator"""

    @expectedFailure
    def test_expected_to_fail(self):
        """This test is expected to fail (marked as XFAIL)"""
        # This will fail, but it's expected
        self.assertEqual(2, 3, "This is an expected failure")

    @expectedFailure
    def test_actually_passes(self):
        """Test marked as expectedFailure but actually passes (XPASS)"""
        self.assertEqual(2, 2)


class TestAssertsEqual(TestCase):
    """Additional assertion tests"""

    def test_assertAlmostEqual(self):
        """Test assertAlmostEqual for floating point numbers"""
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)

    def test_assertListEqual(self):
        """Test assertListEqual for lists"""
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        self.assertListEqual(list1, list2)

    def test_assertDictEqual(self):
        """Test assertDictEqual for dictionaries"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"a": 1, "b": 2}
        self.assertDictEqual(dict1, dict2)

    def test_assertIsInstance(self):
        """Test assertIsInstance to check type"""
        value = "hello"
        self.assertIsInstance(value, str)


# ===========================
# Test Suite and Loader
# ===========================


def create_suite():
    """Create a custom TestSuite with selected tests"""
    suite = TestSuite()

    # Add specific tests
    suite.addTest(TestBasicAssertions("test_assertEqual"))
    suite.addTest(TestBasicAssertions("test_assertTrue"))
    suite.addTest(TestSetUpTearDown("test_initial_value"))
    suite.addTest(TestSubTest("test_add_multiple_cases"))

    return suite


def load_tests(loader, tests, pattern):
    """
    Custom load_tests function to control which tests are loaded.
    This function is called by unittest discovery.
    """
    suite = TestSuite()

    # Load all tests from specific test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicAssertions))
    suite.addTests(loader.loadTestsFromTestCase(TestSetUpTearDown))
    suite.addTests(loader.loadTestsFromTestCase(TestSubTest))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptions))

    return suite


# ===========================
# Main Entry Point
# ===========================

if __name__ == "__main__":
    # Method 1: Run all tests with unittest.main()
    unittest.main(verbosity=2)

    # Method 2 (commented out): Run custom suite
    # runner = unittest.TextTestRunner(verbosity=2)
    # suite = create_suite()
    # runner.run(suite)

    # Method 3 (commented out): Run with TestLoader
    # loader = TestLoader()
    # suite = loader.loadTestsFromModule(__import__(__name__))
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
