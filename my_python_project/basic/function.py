# Basic function definition with placeholder
def myFunction(a, b):
    pass


# ===== ARGUMENT PASSING METHODS =====

# Positional arguments - values assigned by position
myFunction(1, 2)

# Keyword arguments - values assigned by name
myFunction(b=3, a=5)

# Mix of positional and keyword arguments
myFunction(5, b=6)


# ===== BUILT-IN SORTING EXAMPLES =====

# Sort a list in ascending order (default behavior)
print(sorted([3, 1, 4, 1, 5, 9, 2, 6]))

# Sort in descending order using keyword argument
print(sorted([3, 1, 4, 1, 5, 9, 2, 6], reverse=True))


# ===== KEYWORD-ONLY ARGUMENTS =====


# The asterisk (*) forces all arguments following it to be keyword-only
def myFunction(positional_arg, *, kwonly_arg, kwonly_args):
    print(positional_arg)
    print(kwonly_arg)
    print(kwonly_args)


# Call with keyword-only arguments (must use names)
myFunction(10, kwonly_arg=20, kwonly_args=30)


# ===== DEFAULT PARAMETER VALUES =====


def greet(name, greeting="Hello"):
    """Function with default parameter value"""
    print(f"{greeting}, {name}!")


greet("Alice")  # Uses default greeting
greet("Bob", greeting="Hi")  # Overrides default greeting


# ===== *ARGS - VARIABLE POSITIONAL ARGUMENTS =====


def add_numbers(*numbers):
    """Accept any number of positional arguments"""
    total = sum(numbers)
    return total


print(add_numbers(1, 2, 3))  # Returns 6
print(add_numbers(10, 20, 30, 40))  # Returns 100


# ===== **KWARGS - VARIABLE KEYWORD ARGUMENTS =====


def print_info(**info):
    """Accept any number of keyword arguments"""
    for key, value in info.items():
        print(f"{key}: {value}")


print_info(name="Charlie", age=25, city="New York")


# ===== COMBINING ALL ARGUMENT TYPES =====


def complex_function(pos_arg, *args, kw_only_arg, **kwargs):
    """Demonstrate all argument types together"""
    print(f"Positional: {pos_arg}")
    print(f"Args: {args}")
    print(f"Keyword-only: {kw_only_arg}")
    print(f"Kwargs: {kwargs}")


complex_function(1, 2, 3, 4, kw_only_arg=5, extra1="value1", extra2="value2")


# ===== UNPACKING WITH * OPERATOR =====

my_list = [1, 2, 3]
print(sum(my_list))  # Returns 6


# Unpack a list to pass elements as individual arguments
def sum_numbers(*numbers):
    """Sum variable number of arguments"""
    total = 0
    for num in numbers:
        total += num
    return total


print(sum_numbers(*my_list))  # Unpacks [1, 2, 3] into individual arguments
# Note: * operator works with lists, tuples, sets, and dictionaries


# ===== KEYWORD-ONLY WITH UNPACKING =====


def a(*, s, d):
    """Function requiring keyword-only arguments"""
    print(s)
    print(d)


# This would cause error because function requires keyword arguments
# a(*("a", "b"))  # Doesn't work - passes positional args to keyword-only params


# ===== PACKING AND UNPACKING CONCEPTS =====


def my_function(*args):
    """Packing: multiple values packed into a tuple"""
    print(args)


my_function(1, 2, 3)
my_function("a", "b", "c")
my_function(*(x for x in range(10)))  # Unpack generator into arguments


# Only one *args parameter allowed; keyword-only args must follow
def my_function_1(*args, kw_arg="default"):
    """Mixed packing and keyword-only arguments"""
    print(args)


my_function_1(1, 2, 3)
my_function_1(1, 2, 3, kw_arg="custom")


# ===== UNPACKING DICTIONARIES =====


def kTeam(a, b, c):
    """Function with three parameters"""
    print(a, b, c)


dic = {"a": 1, "b": 2, "c": 3}
kTeam(**dic)  # Unpacks dictionary keys as keyword arguments


# ===== COLLECTING KEYWORD ARGUMENTS =====


def sTeam(**kwargs):
    """Collect keyword arguments into a dictionary"""
    print(kwargs)


sTeam(a=1, b=2, c=3)
