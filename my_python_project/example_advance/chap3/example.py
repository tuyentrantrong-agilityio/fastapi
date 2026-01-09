"""
NAMING CONVENTIONS AND CODE STYLE IN PYTHON
============================================

This module demonstrates Python's naming conventions and best practices
for writing clean, readable code according to PEP 8 style guide.
"""

# ============================================================================
# 1. CONSTANT NAMING CONVENTION: Use UPPERCASE for module-level constants
# ============================================================================

# PROBLEM: Using lowercase for constants makes it unclear if the variable
# should be modified or is a fixed value.

# Bad example (do NOT do this):
# seconds_in_a_day = 60 * 60 * 24
# Questions when reading code:
#   - Can this variable be reassigned?
#   - Where was this variable defined?
#   - Should I modify it elsewhere?
#   - Is it a constant or a regular variable?
#   Result: Confusion and harder code maintenance!

# SOLUTION: Use UPPERCASE with underscores for all module-level constants
SECONDS_IN_A_DAY = 60 * 60 * 24
# Now it's IMMEDIATELY CLEAR:
#   - This is a constant, DO NOT modify it
#   - It's defined at module-level
#   - Python doesn't have a const keyword, so we follow the convention:
#   - UPPERCASE with underscores = constant value

# ============================================================================
# 2. QUICK REFERENCE: Python Naming Conventions (PEP 8)
# ============================================================================


# Class names          → CamelCase
#   Example: StringManipulator, DataProcessor
class DataProcessor:
    pass


# Function names       → snake_case
#   Example: calculate_mean(), get_user_name()
def calculate_mean(numbers):
    """Calculate the mean of a list of numbers."""
    return sum(numbers) / len(numbers)


# Variable names       → snake_case
#   Example: total_count, user_name, is_active
total_count = 100
user_name = "Alice"
is_active = True

# Constant names       → ALL_CAPS
#   Example: MAX_RETRIES, DEFAULT_TIMEOUT, SECONDS_IN_A_DAY
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# ============================================================================
# 3. WHY NOT USE ABBREVIATIONS IN VARIABLE NAMES?
# ============================================================================

# BAD - Abbreviated names (hard to understand):
# cnt = 5
# tmp_val = 10
# usr_nm = "Bob"
# Problems:
#   - You read code much more than you write it
#   - Code is meant for humans to read, not machines to parse
#   - Abbreviated names reduce code clarity

# GOOD - Full, descriptive names:
count = 5  # Clear what we're counting
temporary_value = 10  # Immediately obvious it's temporary
user_name = "Bob"  # No guessing about what "usr_nm" means

# Example: Calculating total time
"""
# Bad:
cnt = 0
for i in lst:
    cnt += i

# Good:
total_count = 0
for item in items_list:
    total_count += item
"""

# ============================================================================
# 4. ONE STATEMENT PER LINE - Avoid cramming code into one line
# ============================================================================

# BAD - Multiple statements on one line (WRONG):
my_list = [1, 2, 3, 4, 5]
# for element in my_list: print(element); print('-' * 20)
# Problems:
#   - Hard to read and understand logic flow
#   - Difficult to debug line by line
#   - Violates Python philosophy (Zen of Python)
#   - Hard to add breakpoints in debugger

# GOOD - One clear action per line (CORRECT):
my_list = [1, 2, 3, 4, 5]
for element in my_list:
    print(element)
    print("-" * 20)

# GOLDEN RULE:
# → Don't use semicolons (;) unless absolutely necessary
# → Each line should contain ONE logical action
# → Makes code readable and maintainable

# ============================================================================
# 5. DOCUMENTATION - Writing Docstrings (PEP 257)
# ============================================================================

# WHAT IS A DOCSTRING?
# A docstring is a string literal placed immediately after a function/class/module
# definition to document it. It's different from a regular comment (#).


# Example of a docstring:
def add_numbers(a, b):
    """Add two numbers and return the result.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b


# WHY USE DOCSTRINGS INSTEAD OF COMMENTS?
# ✓ IDEs recognize docstrings and show them as tooltips
# ✓ Tools like Sphinx can automatically generate documentation
# ✓ Help systems can access docstrings
# ✗ Regular # comments don't have these features


# BAD - Using regular comments (NOT a docstring):
def calculate_statistics(value_list):
    # calculates various statistics for a list of numbers
    return {"mean": sum(value_list) / len(value_list)}


# Problem: IDE won't recognize this as documentation


# GOOD - Using proper docstring format:
def calculate_statistics_proper(value_list):
    """Calculate statistical measures for a list of numbers.

    Args:
        value_list: A list of numeric values

    Returns:
        dict: Contains mean, median, and mode of the values
    """
    mean = sum(value_list) / len(value_list)
    return {"mean": mean}


# DOCSTRING GUIDELINES (90% rule):
# 1. Every public function/class should have a docstring
# 2. First line = short description (one sentence)
# 3. If longer, add blank line, then detailed explanation
# 4. Use proper formatting for arguments and return values


# Example of well-formatted docstring:
def find_maximum(numbers):
    """Return the largest number in a list.

    This function iterates through all numbers and tracks the maximum value.
    It handles both positive and negative numbers.

    Args:
        numbers: List of integers or floats to search through

    Returns:
        int or float: The largest value in the list

    Raises:
        ValueError: If the list is empty

    Example:
        >>> find_maximum([1, 5, 3, 2])
        5
    """
    if not numbers:
        raise ValueError("List cannot be empty")
    return max(numbers)


# ============================================================================
# 6. AVOID LINE-BY-LINE COMMENTS - Self-explaining code is better
# ============================================================================

# BAD - Over-commenting obvious code:
# iterate over each number
for number in [1, 2, 3, 4, 5]:
    # add it to total
    total = sum([1, 2, 3, 4, 5])
    # print the result
    print(total)
# Problems:
#   - Too many comments for obvious operations
#   - Comments can become outdated when code changes
#   - Comments on EVERY line suggest code is unclear
#   - Clutters the code and reduces readability


# GOOD - Let the code speak for itself:
def calculate_mean(numbers):
    """Calculate the average of a list of numbers."""
    return sum(numbers) / len(numbers)


total = calculate_mean([1, 2, 3, 4, 5])
print(total)

# RULE: If you need to comment a line to explain it → REWRITE that line!
# Code should be so clear that comments are rarely needed.

# ============================================================================
# 7. DOCUMENT "WHAT", NOT "HOW" - Focus on purpose, not implementation
# ============================================================================


# BAD - Describing the algorithm (HOW):
def check_prime(n):
    """
    Iterate from 2 to n-1, if any number divides n evenly
    and the remainder is never 0, return True
    """
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


# Problem:
#   - Describes the algorithm step-by-step
#   - If you change the algorithm later, docstring becomes wrong
#   - Reader doesn't understand the PURPOSE


# GOOD - Describing the purpose (WHAT):
def is_prime(n):
    """Return True if n is a prime number.

    A prime number is a natural number greater than 1
    that has no positive divisors other than 1 and itself.

    Args:
        n: Integer to check

    Returns:
        bool: True if n is prime, False otherwise
    """
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


# PRINCIPLE:
# ✓ WHAT: Describe the goal and what the function returns
# ✗ HOW: Don't describe loops, conditions, or algorithm details
# Reader needs to know PURPOSE, not implementation details
# If you change implementation, docstring stays valid


# ============================================================================
# 8. ORGANIZING IMPORTS - Order matters for readability
# ============================================================================

# CORRECT ORDER (according to PEP 8):
# 1. Standard library imports
# 2. Third-party library imports
# 3. Local/project imports
# Each group separated by a blank line

# Example of proper import organization:
"""
import os                          # Standard library
import sys                         # Standard library
from datetime import datetime      # Standard library

import requests                    # Third-party
import django                      # Third-party
from flask import Flask            # Third-party

from my_project.models import User          # Local project
from my_project.utils import helper_func    # Local project
"""

# WHY THIS ORDER?
# → When you open a file, you immediately see what dependencies it has
# → Makes it easier to spot missing dependencies
# → IDEs and tools understand this structure better
# → Consistent with Python community standards

# ============================================================================
# 9. USE ABSOLUTE IMPORTS, NOT RELATIVE IMPORTS
# ============================================================================

# BAD - Relative imports (hard to understand):
# from ..other_module import calculate
# Problems:
#   - Hard to read, unclear where calculate() comes from
#   - Difficult to search for usage
#   - Hard to debug
#   - Not explicit about module hierarchy

# GOOD - Absolute imports (clear and explicit):
# import my_project.other_module as other_module
# result = other_module.calculate()
# Or:
# from my_project.other_module import calculate
# result = calculate()

# Advantages of absolute imports:
# ✓ Clear exactly where the function comes from
# ✓ Easy to search the codebase
# ✓ Easy to debug
# ✓ IDE can navigate better
# ✓ Follows PEP 8 recommendation

# ============================================================================
# 10. AVOID WILDCARD IMPORTS - Be explicit about what you import
# ============================================================================

# BAD - Using wildcard imports:
# from math import *
# Problems:
#   - Pollutes the namespace with many names
#   - Risk of naming conflicts with your variables
#   - Can't tell which functions come from where
#   - IDE can't provide proper autocompletion
#   - Makes code harder to understand

# Example of wildcard import problem:
"""
from math import *
from my_custom_module import *

# Now which 'sqrt' am I using? Where did it come from?
result = sqrt(16)
"""

# GOOD - Explicit imports:
# Option 1: Import specific names
from math import sqrt, sin, cos

result = sqrt(16)

# Option 2: Import module and use qualified names
import math

result = math.sqrt(16)

# BEST PRACTICE for multiple imports from same module:
# from django.db.models import (
#     AutoField,
#     BigIntegerField,
#     BooleanField,
#     CharField,
#     DateField,
# )
# Advantages:
# ✓ Clean and organized
# ✓ Easy to add/remove imports
# ✓ Easy to search
# ✓ Follows PEP 8

# ============================================================================
# 11. OPTIONAL IMPORTS - Handle missing packages gracefully
# ============================================================================

# Sometimes you want to use a package that might not be installed.
# Use try/except to handle this:

# Example: Using cProfile if available, fallback to profile
try:
    import cProfile as profiler
except ImportError:
    import profile as profiler

# Now rest of code always uses 'profiler' regardless of what's available
profiler.run("some_function()")

# Advantages:
# ✓ Code always works, even if optional package is missing
# ✓ Rest of the code doesn't need to check availability
# ✓ Graceful degradation

# ============================================================================
# 12. USING __init__.py TO SIMPLIFY PACKAGE INTERFACE
# ============================================================================

# The __init__.py file in a package directory allows you to:
# 1. Make a directory a Python package
# 2. Control what gets imported when using: from package import *
# 3. Simplify import paths for users

# Example directory structure:
"""
my_package/
    __init__.py      # Makes this a package
    models.py
    utils.py
    handlers.py
"""

# Without __init__.py optimization:
# from my_package.models import User
# from my_package.utils import format_string
# from my_package.handlers import process_request

# With __init__.py content:
# __init__.py
# from .models import User
# from .utils import format_string
# from .handlers import process_request

# Users can now do (simpler!):
# from my_package import User, format_string, process_request

# Advantages:
# ✓ Cleaner imports for users of your package
# ✓ Hide internal module structure
# ✓ Easier to refactor internal organization
# ✓ Better encapsulation
