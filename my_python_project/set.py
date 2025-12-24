# ============================================
# PYTHON SETS - Unordered Collection of Unique Elements
# ============================================

# Example 1: Create a set with duplicate values
# Note: Sets automatically remove duplicate elements
set_1 = {69, 96, 96}
print("Set 1:", set_1)  # Output: {69, 96} - duplicate removed
print("Type:", type(set_1))  # Output: <class 'set'>
print()

# Example 2: Create an empty set using the set() constructor
# This is the correct way to create an empty set
set_2 = set()
print("Empty Set:", set_2)  # Output: set()
print("Type:", type(set_2))  # Output: <class 'set'>
print()

# Example 3: Using {} creates a dictionary, NOT an empty set
# To create an empty set, you MUST use set()
set_3 = {}
print("Empty Dictionary (NOT a set):", set_3)  # Output: {}
print("Type:", type(set_3))  # Output: <class 'dict'>
print()

# Example 4: Create a set using set comprehension
# This creates a set of numbers from 0 to 2
set_4 = {value for value in range(3)}
print("Set from comprehension:", set_4)  # Output: {0, 1, 2}
print("Type:", type(set_4))  # Output: <class 'set'>
print()

# Example 5: Create a set from a tuple using the set() constructor
# The constructor converts any iterable (tuple, list, string, etc.) into a set
set_5 = set((3, 2, 1))
print("Set from tuple:", set_5)  # Output: {1, 2, 3} - order may vary
print("Type:", type(set_5))  # Output: <class 'set'>
print()

# Example 6: Check if an element exists in a set using 'in' operator
# This is very efficient for membership testing
print("Is 1 in the set {1, 2, 3}?", 1 in {1, 2, 3})  # Output: True

# You can also check if a tuple exists in a set
print("Is (1, 2) in the set?", (1, 2) in {(1, 2), 3})  # Output: Trueprint()

# ============================================
# SET METHODS - Modifying Sets
# ============================================

# Method 1: add() - Add a single element to the set
print("--- Method 1: add() ---")
fruits = {"apple", "banana", "orange"}
print("Original set:", fruits)
fruits.add("mango")
print("After add('mango'):", fruits)
print()

# Method 2: remove() - Remove an element (raises KeyError if not found)
print("--- Method 2: remove() ---")
fruits = {"apple", "banana", "orange"}
print("Original set:", fruits)
fruits.remove("banana")
print("After remove('banana'):", fruits)
# fruits.remove("grape")  # This would raise KeyError!
print()

# Method 3: discard() - Remove an element safely (no error if not found)
print("--- Method 3: discard() ---")
fruits = {"apple", "banana", "orange"}
print("Original set:", fruits)
fruits.discard("banana")
print("After discard('banana'):", fruits)
fruits.discard("grape")  # No error - safely ignored
print("After discard('grape'):", fruits)
print()

# Method 4: pop() - Remove and return an arbitrary element
print("--- Method 4: pop() ---")
fruits = {"apple", "banana", "orange"}
print("Original set:", fruits)
removed = fruits.pop()
print("Removed element:", removed)
print("Set after pop():", fruits)
print()

# Method 5: clear() - Remove all elements from the set
print("--- Method 5: clear() ---")
fruits = {"apple", "banana", "orange"}
print("Original set:", fruits)
fruits.clear()
print("After clear():", fruits)
print()

# ============================================
# SET METHODS - Set Operations
# ============================================

# Method 6: union() - Combine two sets (no duplicates)
print("--- Method 6: union() ---")
set_a = {1, 2, 3}
set_b = {3, 4, 5}
print("Set A:", set_a)
print("Set B:", set_b)
print("Union (A | B):", set_a.union(set_b))
print("Using | operator:", set_a | set_b)
print()

# Method 7: intersection() - Elements common to both sets
print("--- Method 7: intersection() ---")
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
print("Set A:", set_a)
print("Set B:", set_b)
print("Intersection (A & B):", set_a.intersection(set_b))
print("Using & operator:", set_a & set_b)
print()

# Method 8: difference() - Elements in first set but not in second
print("--- Method 8: difference() ---")
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
print("Set A:", set_a)
print("Set B:", set_b)
print("Difference (A - B):", set_a.difference(set_b))
print("Using - operator:", set_a - set_b)
print()

# Method 9: symmetric_difference() - Elements in either set but not both
print("--- Method 9: symmetric_difference() ---")
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
print("Set A:", set_a)
print("Set B:", set_b)
print("Symmetric Difference (A ^ B):", set_a.symmetric_difference(set_b))
print("Using ^ operator:", set_a ^ set_b)
print()

# ============================================
# SET METHODS - Comparison and Testing
# ============================================

# Method 10: issubset() - Check if set_a is a subset of set_b
print("--- Method 10: issubset() ---")
set_a = {1, 2}
set_b = {1, 2, 3, 4}
print("Set A:", set_a)
print("Set B:", set_b)
print("Is A a subset of B?", set_a.issubset(set_b))  # True
print("Using <= operator:", set_a <= set_b)
print()

# Method 11: issuperset() - Check if set_a is a superset of set_b
print("--- Method 11: issuperset() ---")
set_a = {1, 2, 3, 4}
set_b = {1, 2}
print("Set A:", set_a)
print("Set B:", set_b)
print("Is A a superset of B?", set_a.issuperset(set_b))  # True
print("Using >= operator:", set_a >= set_b)
print()

# Method 12: isdisjoint() - Check if two sets have no common elements
print("--- Method 12: isdisjoint() ---")
set_a = {1, 2, 3}
set_b = {4, 5, 6}
set_c = {3, 4, 5}
print("Set A:", set_a)
print("Set B:", set_b)
print("Are A and B disjoint?", set_a.isdisjoint(set_b))  # True
print("Are A and C disjoint?", set_a.isdisjoint(set_c))  # False
print()

# ============================================
# SET METHODS - Copying and Other Operations
# ============================================

# Method 13: copy() - Create a shallow copy of the set
print("--- Method 13: copy() ---")
original_set = {1, 2, 3}
copied_set = original_set.copy()
print("Original set:", original_set)
print("Copied set:", copied_set)
copied_set.add(4)
print("After adding 4 to copied set:")
print("Original set:", original_set)  # Unchanged
print("Copied set:", copied_set)
print()

# Method 14: len() - Get the number of elements in a set
print("--- Method 14: len() ---")
my_set = {10, 20, 30, 40, 50}
print("Set:", my_set)
print("Number of elements:", len(my_set))
print()

# ============================================
# PRACTICAL EXAMPLE: Remove Duplicates
# ============================================

print("--- Practical Example: Remove Duplicates ---")
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
print("Original list with duplicates:", numbers)
unique_numbers = list(set(numbers))
print("Converted to set and back to list:", sorted(unique_numbers))
print()
