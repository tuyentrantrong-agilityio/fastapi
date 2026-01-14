import unittest


class ListUtils:
    """Simple list utilities for testing"""

    def find_max(self, lst):
        if not lst:
            raise ValueError("List is empty")
        return max(lst)

    def remove_duplicates(self, lst):
        return list(dict.fromkeys(lst))

    def is_sorted(self, lst):
        return lst == sorted(lst)


class TestListUtils(unittest.TestCase):
    def setUp(self):
        self.utils = ListUtils()

    def test_find_max(self):
        self.assertEqual(self.utils.find_max([1, 5, 3, 9, 2]), 9)

    def test_find_max_empty_list(self):
        with self.assertRaises(ValueError):
            self.utils.find_max([])

    def test_remove_duplicates(self):
        self.assertEqual(self.utils.remove_duplicates([1, 2, 2, 3, 3, 3]), [1, 2, 3])

    def test_is_sorted(self):
        self.assertTrue(self.utils.is_sorted([1, 2, 3, 4, 5]))
        self.assertFalse(self.utils.is_sorted([5, 2, 3, 1]))


if __name__ == "__main__":
    unittest.main()
