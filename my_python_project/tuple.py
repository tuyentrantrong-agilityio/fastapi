# ===== Python Tuples - Immutable Sequences =====
# Tuples are immutable sequences enclosed in parentheses ()
# Elements are separated by commas ,
# Tuples can contain any Python data type
# Benefits:
#   - Faster access than lists
#   - Protects data from being modified
#   - Can be used as dictionary keys (hashable)

# 1. Creating a basic tuple
basic_tuple = (
    1,
    2,
    3,
    "python",
    (1, 2, 3),  # Nested tuple
)
print(f"Basic tuple: {basic_tuple}")

# 2. Important: Single element tuples need a trailing comma
single_element = (1,)  # This is a tuple
print(f"Single element tuple: {single_element}, Type: {type(single_element)}")

single_no_comma = 1  # This is just an integer, not a tuple
print(f"Without comma: {single_no_comma}, Type: {type(single_no_comma)}")

# 3. Creating empty tuple
empty_tuple = ()
print(f"Empty tuple: {empty_tuple}")

# 4. Creating tuples using generators and tuple conversion
# Generator expression (lazy evaluation)
tuple_from_generator = tuple(i for i in range(10))
print(f"Tuple from generator: {tuple_from_generator}")

# Tuple with condition
even_numbers = tuple(i for i in range(10) if i % 2 == 0)
print(f"Even numbers tuple: {even_numbers}")

# 5. Tuple operations
# Concatenation with +=
tuple_plus = (1, 5, 9)
print(f"\nOriginal: {tuple_plus}")
tuple_plus += (2, 6, 10)
print(f"After += (2, 6, 10): {tuple_plus}")

# Repetition with *
tuple_multi = (1, 5, 9) * 3
print(f"(1, 5, 9) * 3 = {tuple_multi}")

# 6. Accessing elements
first_element = tuple_multi[0]
print(f"\nFirst element: {first_element}")

# 7. Membership test (in operator)
result = 1 in tuple_plus
print(f"Is 1 in {tuple_plus}? {result}")

# 8. Tuple methods
# count() - counts occurrences of an element
element_count = tuple_multi.count(1)
print(f"\nCount of 1 in {tuple_multi}: {element_count}")

# index() - finds first occurrence of element
index_of_5 = (1, 5, 9).index(5)
print(f"Index of 5 in (1, 5, 9): {index_of_5}")
