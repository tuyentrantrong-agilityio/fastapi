# 1. VARIABLES
x = y = z = "foo"  # Assign one value to multiple variables

# Swap values
a, b = 10, 20
a, b = b, a
print(f"Swapped: a={a}, b={b}")

# ============================================================================
# 2. STRINGS
# ============================================================================
text = "  Hello World  "
print(text.strip().lower().replace("world", "Python"))  # Chain operations

# Join strings (faster than concatenation in loops)
items = ["a", "b", "c"]
result = "".join(items)
print(result)

# String formatting
name, age = "John", 30
print(f"Name: {name}, Age: {age}")

# ============================================================================
# 3. LISTS
# ============================================================================
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
fruits.extend(["mango", "pineapple"])
print(f"List: {fruits}")

# Slicing and comprehension
numbers = list(range(10))
print(f"First 3: {numbers[:3]}, Last 3: {numbers[-3:]}")
squares = [x**2 for x in range(5)]
print(f"Squares: {squares}")

# ============================================================================
# 4. DICTIONARIES
# ============================================================================
person = {"name": "John", "age": 30, "city": "New York"}
person["phone"] = "123-456-7890"  # Add new key
print(person)

# Dictionary iteration
for key, value in person.items():
    print(f"{key}: {value}")

# Dictionary comprehension
square_dict = {x: x**2 for x in range(5)}
print(f"Square dict: {square_dict}")

# ============================================================================
# 5. SETS
# ============================================================================
colors = {"red", "blue", "green"}
colors.add("yellow")
print(f"Colors: {colors}")

# Set operations
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}
print(f"Union: {set1 | set2}")
print(f"Intersection: {set1 & set2}")
print(f"Difference: {set1 - set2}")


# ============================================================================
# 6. TUPLES
# ============================================================================
point = (10, 20)
x, y = point  # Unpacking
print(f"Point: x={x}, y={y}")

# Named tuple (more readable)
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(5, 10)
print(f"Named point: x={p.x}, y={p.y}")


# ============================================================================
# 7. CLASSES
# ============================================================================
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def info(self):
        return f"{self.name} is {self.age} years old"


class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.breed = breed

    def speak(self):
        return f"{self.name} barks: Woof!"


dog = Dog("Buddy", 5, "Golden Retriever")
print(dog.info())
print(dog.speak())


# Class methods and static methods
class Counter:
    count = 0

    def __init__(self, name):
        self.name = name
        Counter.count += 1

    @classmethod
    def from_string(cls, string):
        return cls(string.split(":")[0])

    @staticmethod
    def is_valid(value):
        return isinstance(value, str) and len(value) > 0


c1 = Counter("A")
c2 = Counter("B")
print(f"Total counters: {Counter.count}")

# ============================================================================
# 8. CONTEXT MANAGERS
# ============================================================================
from pathlib import Path

# File handling (auto-closes)
temp_file = Path("temp.txt")
with open(temp_file, "w") as f:
    f.write("Hello, World!")

with open(temp_file, "r") as f:
    print(f.read())

temp_file.unlink()


# Custom context manager
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        print(f"Connecting to {self.db_name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing {self.db_name}...")


with DatabaseConnection("mydb") as db:
    print(f"Connected to {db.db_name}")

# Context manager with decorator
from contextlib import contextmanager


@contextmanager
def managed_resource(name):
    print(f"Acquiring {name}...")
    try:
        yield f"Resource-{name}"
    finally:
        print(f"Releasing {name}...")


with managed_resource("Database") as res:
    print(f"Using: {res}")
