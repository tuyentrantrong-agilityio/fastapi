import unittest


class Person:
    """Simple person class for testing"""

    def __init__(self, name, age):
        if age < 0:
            raise ValueError("Age cannot be negative")
        self.name = name
        self.age = age

    def is_adult(self):
        return self.age >= 18

    def birthday(self):
        self.age += 1


class TestPerson(unittest.TestCase):
    def setUp(self):
        self.person = Person("Alice", 25)

    def test_person_creation(self):
        self.assertEqual(self.person.name, "Alice")
        self.assertEqual(self.person.age, 25)

    def test_invalid_age(self):
        with self.assertRaises(ValueError):
            Person("Bob", -5)

    def test_is_adult(self):
        self.assertTrue(self.person.is_adult())
        child = Person("Charlie", 10)
        self.assertFalse(child.is_adult())

    def test_birthday(self):
        self.person.birthday()
        self.assertEqual(self.person.age, 26)


if __name__ == "__main__":
    unittest.main()
