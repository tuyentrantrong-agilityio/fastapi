# ===== Python Lists - Storing Multiple Values =====
# Lists are mutable sequences that can store multiple values of any type
# List is defined with square brackets []
# Elements are separated by commas ,
# Lists can contain any Python data type

# 1. Creating a basic list
my_list = [1, "a", 5, True]
print(f"Mixed type list: {my_list}")

# 2. Creating lists using different methods
# Method 1: List comprehension
list_comprehension = [i for i in range(5)]
print(f"List from comprehension: {list_comprehension}")

# Method 2: Using range()
list_from_range = list(range(10))
print(f"List from range: {list_from_range}")

# 3. Checking if an element exists in a list
my_list_check = [1, 2, 3, 4]
print(f"Is 'hello' in list? {'hello' in my_list_check}")
print(f"Is 2 in list? {2 in my_list_check}")

# 4. Accessing elements by index
print(f"First element (index 0): {my_list_check[0]}")
print(f"Last element (index -1): {my_list_check[-1]}")

# 5. List methods demonstration
example_list = [1, 2, 3, 4, 5, 6, 78, 9]

# count() - counts occurrences of an element
element_count = example_list.count(1)
print(f"\nCount of 1: {element_count}")

# copy() - creates a shallow copy
list_copy = example_list.copy()
print(f"List copy: {list_copy}")

# append() - adds one element to the end
example_list.append(10)
print(f"After append(10): {example_list}")

# extend() - adds multiple elements
example_list.extend([11, 12, 13, 14])
print(f"After extend: {example_list}")

# insert() - inserts element at specific index
example_list.insert(5, 69)  # Insert 69 at index 5
print(f"After insert(5, 69): {example_list}")

# pop() - removes and returns element at index
popped_value = example_list.pop(0)
print(f"Popped first element: {popped_value}")
print(f"After pop(0): {example_list}")

# remove() - removes first occurrence of value (no return)
example_list.remove(78)
print(f"After remove(78): {example_list}")

# sort() - sorts list in place (only for same data types)
example_list.sort()
print(f"After sort(): {example_list}")

# clear() - removes all elements
# example_list.clear()  # Uncomment to clear the list
# print(f"After clear(): {example_list}")
