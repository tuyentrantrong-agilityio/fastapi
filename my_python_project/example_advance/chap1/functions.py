# 1. Default arguments & mutable objects
# ⚠️ Problem: Using list as default value


def add_item_bad(item, cart=[]):
    cart.append(item)
    return cart


# ❌ WRONG - Default argument is created only once
# Calling function multiple times will share the same list
print(add_item_bad("apple"))  # ['apple']
print(add_item_bad("banana"))  # ['apple', 'banana'] ← alert!
print(add_item_bad("cherry"))  # ['apple', 'banana', 'cherry'] ← old values persist


# ✅ CORRECT - Create new list each time function is called
def add_item(item, cart=None):
    if cart is None:
        cart = []
    cart.append(item)
    return cart


print(add_item("apple"))  # ['apple']
print(add_item("banana"))  # ['banana'] ← clean!
print(add_item("cherry"))  # ['cherry']


# 2. Return - Return result directly
# ❌ WRONG - Use unnecessary intermediate variable
def is_equal_bad(a, b):
    result = False
    if a == b:
        result = True
    return result


# ✅ CORRECT - Return expression result immediately
def is_equal(a, b):
    return a == b


print(is_equal(5, 5))  # True
print(is_equal(5, 3))  # False


# 3. Keyword arguments - Default values
# Use when you want to allow caller to optionally change the value
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")


greet("Tuyen")  # Hello, Tuyen!
greet("Sinh", greeting="Hi")  # Hi, Sinh!
greet("Huyen", greeting="Hola")  # Hola, Huyen!


# 4. *args and **kwargs - Undefined number of parameters

# 4a. *args = Positional arguments grouped into tuple
# Use when you don't know in advance how many parameters will be passed


def sum_numbers(*args):
    """Sum all parameters"""
    total = 0
    for num in args:
        total += num
    return total


print(sum_numbers(1, 2, 3))  # 6
print(sum_numbers(1, 2, 3, 4, 5))  # 15
print(sum_numbers(10))  # 10


# 4b. **kwargs = Keyword arguments grouped into dict
# Use when you want to pass key-value pairs flexibly


def print_info(**kwargs):
    """Print information from keyword arguments"""
    for key, value in kwargs.items():
        print(f"{key}: {value}")


print_info(name="Tuyen", age=25, city="HCM")
# Output:
# name: Tuyen
# age: 25
# city: HCM


# 4c. Combine both *args and **kwargs
def flexible_function(a, b, *args, **kwargs):
    """Flexible function with multiple parameter types"""
    print(f"a = {a}, b = {b}")
    print(f"args = {args}")
    print(f"kwargs = {kwargs}")


flexible_function(1, 2, 3, 4, 5, name="Tuyen", age=25)
# Output:
# a = 1, b = 2
# args = (3, 4, 5)
# kwargs = {'name': 'Tuyen', 'age': 25}


# ⭐ Remember:
# *args  → tuple  (use for positional arguments)
# **kwargs → dict   (use for keyword arguments)
