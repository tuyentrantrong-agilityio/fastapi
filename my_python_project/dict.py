# ============================================
# PYTHON DICTIONARIES - Key-Value Pairs
# ============================================

# Example 1: Create and access dictionary values
# A dictionary stores data as key-value pairs
dic = {"name": "Tuyen", "age": 36, "country": "Vietnam"}
print("Dictionary:", dic)
print("Name: ", dic["name"])  # Access value using key
print("Age: ", dic["age"])  # Output: 36
print("Country: ", dic["country"])  # Output: Vietnam
print()

# Example 2: Create an empty dictionary using curly braces {}
dic_1 = {}
print("Empty Dictionary:", dic_1)
print("Type:", type(dic_1))  # Output: <class 'dict'>
print()

# Example 3: Create an empty dictionary using dict() constructor
dic_2 = dict()
print("Empty Dictionary:", dic_2)  # Output: {}
print("Type:", type(dic_2))  # Output: <class 'dict'>
print()

# Example 4: Create dictionary using dict() constructor with keyword arguments
# This is a convenient way to create dictionaries with string keys
dic_3 = dict(name="Banhmi", member="saigon")
print(
    "Dictionary from constructor:", dic_3
)  # Output: {'name': 'Banhmi', 'member': 'saigon'}
print("Type:", type(dic_3))
print()

# Example 5: Create dictionary using fromkeys() - Initialize with default values
# This creates a dictionary with the same value for all keys
iter = {"name", "number", "country"}
dic_none = dict.fromkeys(iter, "Sync value")
print("Dictionary with fromkeys():", dic_none)
# Output: {'name': 'Sync value', 'number': 'Sync value', 'country': 'Sync value'}
print()

# Example 6: Dictionary with different types as keys
# Dictionary keys can be strings, numbers, or tuples (any immutable type)
d = {"name": "Tuyen", "age": 36, (1, 2): 69}
print("Dictionary with tuple key:", d)
print()

# ============================================
# DICTIONARY METHODS - Accessing Data
# ============================================

# Method 1: get() - Safely access values without raising KeyError
print("--- Method 1: get() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
print("Value for 'name':", student.get("name"))  # Output: John
print("Value for 'address':", student.get("address"))  # Output: None (no error)
print("Value for 'address' with default:", student.get("address", "Not found"))
print()

# Method 2: keys() - Get all dictionary keys
print("--- Method 2: keys() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
keys = student.keys()
print("All keys:", keys)  # Output: dict_keys(['name', 'age', 'grade'])
print("Keys as list:", list(keys))
print()

# Method 3: values() - Get all dictionary values
print("--- Method 3: values() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
values = student.values()
print("All values:", values)  # Output: dict_values(['John', 20, 'A'])
print("Values as list:", list(values))
print()

# Method 4: items() - Get all key-value pairs as tuples
print("--- Method 4: items() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
items = student.items()
print(
    "All items:", items
)  # Output: dict_items([('name', 'John'), ('age', 20), ('grade', 'A')])
print("Items as list:", list(items))
print()

# ============================================
# DICTIONARY METHODS - Modifying Data
# ============================================

# Method 5: update() - Add or update multiple key-value pairs
print("--- Method 5: update() ---")
student = {"name": "John", "age": 20}
print("Original:", student)
student.update({"age": 21, "grade": "A"})
print("After update():", student)
print()

# Method 6: pop() - Remove and return value by key
print("--- Method 6: pop() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Original:", student)
removed_value = student.pop("grade")
print("Removed value:", removed_value)  # Output: A
print("After pop():", student)
print()

# Method 7: popitem() - Remove and return last inserted key-value pair
print("--- Method 7: popitem() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Original:", student)
removed_pair = student.popitem()
print("Removed pair:", removed_pair)  # Output: ('grade', 'A')
print("After popitem():", student)
print()

# Method 8: clear() - Remove all items from dictionary
print("--- Method 8: clear() ---")
d = {"name": "Tuyen", "age": 36}
print("Original:", d)
d.clear()
print("After clear():", d)  # Output: {}
print()

# Method 9: setdefault() - Set value if key doesn't exist, return value
print("--- Method 9: setdefault() ---")
student = {"name": "John", "age": 20}
print("Original:", student)
result1 = student.setdefault("age", 25)  # Key exists, return existing value
print("setdefault('age', 25):", result1)  # Output: 20
result2 = student.setdefault("grade", "A")  # Key doesn't exist, set it
print("setdefault('grade', 'A'):", result2)  # Output: A
print("After setdefault():", student)
print()

# ============================================
# DICTIONARY METHODS - Copying and Comparison
# ============================================

# Method 10: copy() - Create a shallow copy of dictionary
print("--- Method 10: copy() ---")
original = {"name": "John", "age": 20}
copied = original.copy()
print("Original:", original)
print("Copied:", copied)
copied["age"] = 21
print("After modifying copy:")
print("Original:", original)  # Unchanged
print("Copied:", copied)
print()

# ============================================
# ITERATING THROUGH DICTIONARIES
# ============================================

# Method 11: Iterate through keys
print("--- Iterate through keys ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
print("Iterating through keys:")
for key in student:
    print(f"  {key}")
print()

# Method 12: Iterate through key-value pairs
print("--- Iterate through items with items() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
print("Iterating through items:")
for key, value in student.items():
    print(f"  {key}: {value}")
print()

# ============================================
# CHECKING AND COUNTING
# ============================================

# Method 13: Check if key exists in dictionary
print("--- Check key existence ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
print("Is 'name' in dictionary?", "name" in student)  # Output: True
print("Is 'address' in dictionary?", "address" in student)  # Output: False
print()

# Method 14: len() - Get number of items in dictionary
print("--- Method 14: len() ---")
student = {"name": "John", "age": 20, "grade": "A"}
print("Dictionary:", student)
print("Number of items:", len(student))  # Output: 3
print()

# ============================================
# PRACTICAL EXAMPLES
# ============================================

# Example 1: Count word frequency using dictionary
print("--- Practical Example 1: Word Frequency ---")
text = "python python java java java cpp"
words = text.split()
frequency = {}
for word in words:
    frequency[word] = frequency.get(word, 0) + 1
print("Text:", text)
print("Word frequency:", frequency)
print()

# Example 2: Dictionary to store student information
print("--- Practical Example 2: Student Database ---")
students = {
    "S001": {"name": "John", "age": 20, "major": "CS"},
    "S002": {"name": "Jane", "age": 21, "major": "Math"},
    "S003": {"name": "Bob", "age": 20, "major": "Physics"},
}
print("Student Database:")
for student_id, info in students.items():
    print(f"  {student_id}: {info['name']}, Age: {info['age']}, Major: {info['major']}")
print()
