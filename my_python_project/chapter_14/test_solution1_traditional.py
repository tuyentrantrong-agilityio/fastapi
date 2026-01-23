"""Traditional unittest for solution1.py - Make rhyming words"""

import unittest
from solution1 import (
    get_prefixes,
    stemmer,
    create_rhymes,
    format_rhymes_output,
    format_no_rhyme_message,
)


class TestGetPrefixes(unittest.TestCase):
    """Test cases for get_prefixes function"""

    def setUp(self):
        """Set up test fixtures"""
        self.prefixes = get_prefixes()

    def tearDown(self):
        """Clean up after test"""
        pass

    def test_prefixes_is_list(self):
        """Test that get_prefixes returns a list"""
        self.assertIsInstance(self.prefixes, list)

    def test_prefixes_contains_single_consonants(self):
        """Test that prefixes contains single consonants"""
        for consonant in "bcdfghjklmnpqrstvwxyz":
            self.assertIn(consonant, self.prefixes)

    def test_prefixes_contains_clusters(self):
        """Test that prefixes contains consonant clusters"""
        self.assertIn("ch", self.prefixes)
        self.assertIn("sh", self.prefixes)
        self.assertIn("str", self.prefixes)

    def test_prefixes_length(self):
        """Test that prefixes has expected number of items"""
        self.assertEqual(len(self.prefixes), 57)

    def test_prefixes_are_lowercase(self):
        """Test that all prefixes are lowercase"""
        for prefix in self.prefixes:
            self.assertEqual(prefix, prefix.lower())


class TestStemmer(unittest.TestCase):
    """Test cases for stemmer function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_cases = {
            "cake": ("c", "ake"),
            "apple": ("", "apple"),
            "CHAIR": ("ch", "air"),
            "string": ("str", "ing"),
            "eat": ("", "eat"),
        }

    def tearDown(self):
        """Clean up after test"""
        self.test_cases = None

    def test_stemmer_cake(self):
        """Test stemming 'cake'"""
        prefix, rest = stemmer("cake")
        self.assertEqual(prefix, "c")
        self.assertEqual(rest, "ake")

    def test_stemmer_apple(self):
        """Test stemming 'apple' (starts with vowel)"""
        prefix, rest = stemmer("apple")
        self.assertEqual(prefix, "")
        self.assertEqual(rest, "apple")

    def test_stemmer_uppercase(self):
        """Test stemming uppercase word"""
        prefix, rest = stemmer("CHAIR")
        self.assertEqual(prefix, "ch")
        self.assertEqual(rest, "air")

    def test_stemmer_with_punctuation(self):
        """Test stemming word with punctuation"""
        prefix, rest = stemmer("cake.")
        self.assertEqual(prefix, "c")
        self.assertEqual(rest, "ake")

    def test_stemmer_string_cluster(self):
        """Test stemming word with consonant cluster"""
        prefix, rest = stemmer("string")
        self.assertEqual(prefix, "str")
        self.assertEqual(rest, "ing")

    def test_stemmer_single_vowel(self):
        """Test stemming single vowel"""
        prefix, rest = stemmer("a")
        self.assertEqual(prefix, "")
        self.assertEqual(rest, "a")

    def test_stemmer_returns_tuple(self):
        """Test that stemmer returns a tuple"""
        result = stemmer("test")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


class TestCreateRhymes(unittest.TestCase):
    """Test cases for create_rhymes function"""

    def setUp(self):
        """Set up test fixtures"""
        self.prefixes = ["b", "c", "f", "ch", "sh"]
        self.rest = "ake"
        self.start = "c"

    def tearDown(self):
        """Clean up after test"""
        self.prefixes = None
        self.rest = None
        self.start = None

    def test_create_rhymes_basic(self):
        """Test basic rhyme creation"""
        rhymes = create_rhymes(self.rest, self.start, self.prefixes)
        expected = ["bake", "chake", "fake", "shake"]
        self.assertEqual(rhymes, expected)

    def test_create_rhymes_excludes_start(self):
        """Test that start prefix is excluded"""
        rhymes = create_rhymes(self.rest, self.start, self.prefixes)
        self.assertNotIn("cake", rhymes)

    def test_create_rhymes_is_sorted(self):
        """Test that rhymes are sorted"""
        rhymes = create_rhymes(self.rest, self.start, self.prefixes)
        self.assertEqual(rhymes, sorted(rhymes))

    def test_create_rhymes_returns_list(self):
        """Test that create_rhymes returns a list"""
        rhymes = create_rhymes(self.rest, self.start, self.prefixes)
        self.assertIsInstance(rhymes, list)

    def test_create_rhymes_empty_prefixes(self):
        """Test with empty prefixes list"""
        rhymes = create_rhymes(self.rest, self.start, [])
        self.assertEqual(rhymes, [])

    def test_create_rhymes_single_prefix(self):
        """Test with single prefix"""
        rhymes = create_rhymes(self.rest, "b", ["b", "c"])
        self.assertEqual(rhymes, ["cake"])


class TestFormatRhymesOutput(unittest.TestCase):
    """Test cases for format_rhymes_output function"""

    def setUp(self):
        """Set up test fixtures"""
        self.rhymes_list = ["bake", "cake", "fake"]

    def tearDown(self):
        """Clean up after test"""
        self.rhymes_list = None

    def test_format_rhymes_output_basic(self):
        """Test basic rhyme formatting"""
        output = format_rhymes_output(self.rhymes_list)
        expected = "bake\ncake\nfake"
        self.assertEqual(output, expected)

    def test_format_rhymes_output_single_word(self):
        """Test formatting single word"""
        output = format_rhymes_output(["bake"])
        self.assertEqual(output, "bake")

    def test_format_rhymes_output_returns_string(self):
        """Test that output is a string"""
        output = format_rhymes_output(self.rhymes_list)
        self.assertIsInstance(output, str)

    def test_format_rhymes_output_empty_list(self):
        """Test with empty list"""
        output = format_rhymes_output([])
        self.assertEqual(output, "")

    def test_format_rhymes_output_contains_newlines(self):
        """Test that output contains correct number of newlines"""
        output = format_rhymes_output(self.rhymes_list)
        self.assertEqual(output.count("\n"), 2)


class TestFormatNoRhymeMessage(unittest.TestCase):
    """Test cases for format_no_rhyme_message function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_word = "xyz"

    def tearDown(self):
        """Clean up after test"""
        self.test_word = None

    def test_format_no_rhyme_message_basic(self):
        """Test no rhyme message formatting"""
        message = format_no_rhyme_message(self.test_word)
        expected = "Cannot rhyme with xyz"
        self.assertEqual(message, expected)

    def test_format_no_rhyme_message_returns_string(self):
        """Test that message is a string"""
        message = format_no_rhyme_message("test")
        self.assertIsInstance(message, str)

    def test_format_no_rhyme_message_contains_word(self):
        """Test that message contains the original word"""
        message = format_no_rhyme_message("rhino")
        self.assertIn("rhino", message)

    def test_format_no_rhyme_message_contains_cannot(self):
        """Test that message contains 'Cannot'"""
        message = format_no_rhyme_message("test")
        self.assertIn("Cannot", message)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.prefixes = get_prefixes()

    def tearDown(self):
        """Clean up after test"""
        self.prefixes = None

    def test_stemmer_with_rhymes_cake(self):
        """Test stemmer result with create_rhymes for 'cake'"""
        start, rest = stemmer("cake")
        rhymes = create_rhymes(rest, start, self.prefixes)

        self.assertIn("bake", rhymes)
        self.assertIn("fake", rhymes)
        self.assertNotIn("cake", rhymes)
        self.assertTrue(len(rhymes) > 0)

    def test_stemmer_with_rhymes_string(self):
        """Test stemmer result with create_rhymes for 'string'"""
        start, rest = stemmer("string")
        rhymes = create_rhymes(rest, start, self.prefixes)

        self.assertIn("bing", rhymes)
        self.assertIn("ding", rhymes)
        self.assertIn("fling", rhymes)
        self.assertNotIn("string", rhymes)

    def test_full_workflow_valid_word(self):
        """Test full workflow with valid rhyming word"""
        start, rest = stemmer("phone")
        rhymes = create_rhymes(rest, start, self.prefixes)
        output = format_rhymes_output(rhymes)

        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)

    def test_full_workflow_vowel_word(self):
        """Test full workflow with word starting with vowel"""
        start, rest = stemmer("apple")

        if rest:
            rhymes = create_rhymes(rest, start, self.prefixes)
            output = format_rhymes_output(rhymes)
        else:
            output = format_no_rhyme_message("apple")

        self.assertIsInstance(output, str)


if __name__ == "__main__":
    unittest.main()
