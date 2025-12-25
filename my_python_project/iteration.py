# ============================================================================
# ITERATION IN PYTHON
# ============================================================================
# Iteration is the process of accessing each element one by one from a
# collection of items. Iterators allow you to loop through data efficiently.

print("=" * 60)
print("1. CREATING AND USING ITERATORS")
print("=" * 60)

# Creating an iterator using a generator expression
# This creates an iterator that generates numbers 0, 1, 2
itera = (x for x in range(3))
print(f"Iterator object: {itera}")
print("The iterator object itself shows: <generator object...>")
print()

# Using next() to get elements one by one from the iterator
# Each call to next() moves to the next element
print("Getting elements from iterator using next():")
print(f"First element: {next(itera)}")  # Returns 0
print(f"Second element: {next(itera)}")  # Returns 1
print(f"Third element: {next(itera)}")  # Returns 2

# This would cause an error because the iterator is exhausted:
# print(next(itera))  # StopIteration error!

print("\nNote: You cannot access iterator items by index like itera[0]")
print("Iterators are designed to access items sequentially only.")
print()

# ============================================================================
print("=" * 60)
print("2. ITERATOR BEHAVIOR: REFERENCE VS VALUE")
print("=" * 60)

# When you assign an iterator to a variable, both refer to the same object
original_list = [10, 20, 30, 40]
iter1 = iter(original_list)
iter2 = iter1

print(f"Original list: {original_list}")
print("Both iter1 and iter2 point to the SAME iterator object")
print(f"Next from iter1: {next(iter1)}")  # Returns 10
print(f"Next from iter2: {next(iter2)}")  # Returns 20 (same position!)
print()

# ============================================================================
print("=" * 60)
print("3. SUMMING ITERATOR VALUES")
print("=" * 60)

# Create a fresh iterator with numbers 0, 1, 2
numbers_iter = (x for x in range(3))
print("Fresh iterator created from range(3): [0, 1, 2]")

# sum() adds all elements: 0 + 1 + 2 = 3
total = sum(numbers_iter)
print(f"Sum of all elements: {total}")
print()

# After sum() exhausts the iterator, it cannot be used again
# Create a new iterator to demonstrate the start parameter
numbers_iter = (x for x in range(3))
# sum(iterable, start=value) adds the start value to the sum
total_with_start = sum(numbers_iter, 10)
print(f"Sum with start value of 10: {total_with_start}")  # 0 + 1 + 2 + 10 = 13
print("(After sum(), the iterator is exhausted)")
print()

# ============================================================================
print("=" * 60)
print("4. FINDING MAXIMUM AND MINIMUM")
print("=" * 60)

# Create iterators with values to find max and min
max_iter = (x for x in range(5, 10))  # [5, 6, 7, 8, 9]
print("Iterator with values: [5, 6, 7, 8, 9]")
print(f"Maximum value: {max(max_iter)}")
print()

# For an empty iterator, use default parameter
empty_iter = (x for x in range(0))  # Empty iterator
print("Empty iterator has no values")
print(f"Max with default=50: {max(empty_iter, default=50)}")
print()

# Finding minimum value
min_iter = (x for x in [3, 1, 4, 1, 5, 9, 2, 6])
print("Iterator with values: [3, 1, 4, 1, 5, 9, 2, 6]")
print(f"Minimum value: {min(min_iter)}")
print()

# Empty iterator with default
empty_iter2 = (x for x in [])
print(f"Min of empty iterator with default=0: {min(empty_iter2, default=0)}")
print()

# ============================================================================
print("=" * 60)
print("5. SORTING ITERATORS AND LISTS")
print("=" * 60)

# sorted() returns a new sorted list and can work with iterators
numbers = [1, 3, 6, 5, 6, 2, 8, 4]
print(f"Original list: {numbers}")

# Sort in ascending order (default)
ascending = sorted(numbers, reverse=False)
print(f"Sorted ascending: {ascending}")

# Sort in descending order
descending = sorted(numbers, reverse=True)
print(f"Sorted descending: {descending}")
print()

# sorted() works with iterators too
number_iter = (x for x in [7, 2, 9, 1, 5])
sorted_from_iter = sorted(number_iter)
print(f"Iterator [7, 2, 9, 1, 5] sorted: {sorted_from_iter}")
print()

# ============================================================================
print("=" * 60)
print("6. PRACTICAL EXAMPLE: PROCESSING DATA WITH ITERATORS")
print("=" * 60)

# Example: Process student scores
scores = [78, 92, 85, 88, 76, 95]
print(f"Student scores: {scores}")

# Using iterator to process data
scores_iter = (x for x in scores)
average_score = sum(scores_iter) / len(scores)
print(f"Average score: {average_score:.2f}")

# Create a new iterator for other operations
scores_iter = iter(scores)
print(f"Highest score: {max(scores_iter)}")

scores_iter = iter(scores)
print(f"Lowest score: {min(scores_iter)}")

scores_iter = iter(scores)
sorted_scores = sorted(scores_iter)
print(f"Sorted scores: {sorted_scores}")
