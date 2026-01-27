# ===== Understanding Hashable vs Unhashable Objects =====

# Hashable objects: immutable, can be used as dictionary keys
# Unhashable objects: mutable, cannot be used as dictionary keys

# 1. Getting object ID (memory address)
id_value = id(5)
print(f"ID of 5: {id_value}")

# 2. Integers are immutable, but operations create new objects
n = 69
print(f"Original value: {n}")
print(f"n + 1 = {n + 1}")
print(f"Using __add__ method: {n.__add__(2)}")
# Note: n itself remains unchanged after these operations

# 3. Examples of hashable objects (immutable)
s_1 = "python"  # Strings are hashable
s_2 = "learn"
t_1 = (1, 2, 3)  # Tuples are hashable

# Examples of unhashable objects (mutable)
list_1 = [1, 2, 3]  # Lists are unhashable
dict_1 = {"key": "value"}  # Dictionaries are unhashable

# 4. Demonstrating hashable vs unhashable
print(f"\nString hash: {hash(s_1)}")
print(f"Tuple hash: {hash(t_1)}")
# print(hash(list_1))  # This would raise TypeError - lists can't be hashed
# print(hash(dict_1))  # This would raise TypeError - dicts can't be hashed

# 5. Using as dictionary keys (only hashable objects allowed)
my_dict = {
    s_1: "This is a hashable key",
    t_1: "Tuples can also be keys",
    # list_1: "This would cause an error"  # Lists cannot be dictionary keys
}
