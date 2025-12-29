def myFunction(a, b):
    pass  # placeholder command

# Positional arguments - values assigned by position
myFunction(1, 2)

# Keyword arguments - values assigned by name
myFunction(b=3, a=5)

# Mix of positional and keyword arguments
myFunction(5, b=6)

# Sort a list in ascending order (default behavior)
print(sorted([3, 1, 4, 1, 5, 9, 2, 6]))

# Cannot use positional argument for reverse parameter
print(sorted([3, 1, 4, 1, 5, 9, 2, 6], reverse=True))


# The asterisk (*) is not a parameter itself
# It signals that all arguments following it must be keyword-only arguments
def myFunction(positional_arg, *, kwonly_arg, kwonly_args):
    print(positional_arg)
    print(kwonly_arg)
    print(kwonly_args)

# Call with keyword-only arguments
myFunction(10, kwonly_arg=20, kwonly_args=30)


# Case 1: Function with default parameter values
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")  # Uses default greeting
greet("Bob", greeting="Hi")  # Overrides default greeting


# Case 2: Function with *args (variable positional arguments)
def add_numbers(*numbers):
    total = sum(numbers)
    return total

print(add_numbers(1, 2, 3))  # Returns 6
print(add_numbers(10, 20, 30, 40))  # Returns 100


# Case 3: Function with **kwargs (variable keyword arguments)
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Charlie", age=25, city="New York")


# Case 4: Combining positional, *args, keyword-only, and **kwargs
def complex_function(pos_arg, *args, kw_only_arg, **kwargs):
    print(f"Positional: {pos_arg}")
    print(f"Args: {args}")
    print(f"Keyword-only: {kw_only_arg}")
    print(f"Kwargs: {kwargs}")

complex_function(1, 2, 3, 4, kw_only_arg=5, extra1="value1", extra2="value2")