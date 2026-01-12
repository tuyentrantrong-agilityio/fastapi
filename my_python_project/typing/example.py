# Import all typing utilities at the top
from typing import (
    Any,
    Callable,
    Generator,
    NewType,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

# ============================================================================
# 1. What is typing?
# ============================================================================
# The typing module provides type hints system to clearly specify data types
# of variables, parameters, return values, etc. in Python.
# Important: Python does NOT enforce types at runtime!
# Type hints only help:
# - IDEs and editors display suggestions
# - Type checking tools (like mypy/pyright) detect type-related errors


# Example: Basic function with type hints
def greet(name: str) -> str:
    """
    Greet a person by name.

    Args:
        name: The person's name (must be a string)

    Returns:
        A greeting message (string)
    """
    return "Hello, " + name


# Test the function
print(greet("Alice"))  # Output: Hello, Alice
print(greet("Bob"))  # Output: Hello, Bob

# ============================================================================
# 2. Type Alias - When to use it?
# ============================================================================
# Type alias allows you to define a name for a complex type to make code
# more readable and easier to maintain.

# Example: Using type alias for vector operations
Vector = list[float]


def scale(scalar: float, vector: Vector) -> Vector:
    """
    Scale a vector by multiplying each element by a scalar value.

    Args:
        scalar: The scaling factor (float)
        vector: A list of float values representing the vector

    Returns:
        A new scaled vector
    """
    return [scalar * x for x in vector]


# Test the function
v1 = [1.0, 2.0, 3.0]
v2 = scale(2.5, v1)
print(f"Original vector: {v1}")
print(f"Scaled vector (2.5x): {v2}")  # Output: [2.5, 5.0, 7.5]

# Instead of writing list[float] everywhere, using Vector is cleaner and more readable

# ============================================================================
# 3. Newtype - Create a distinct type
# ============================================================================
# Newtype allows you to create a new type that is distinct from its base type
# This helps prevent accidental type mismatches during type checking.

UserId = NewType("UserId", int)


def fetch_user(uid: UserId) -> str:
    """
    Fetch user information by their ID.

    Args:
        uid: The unique user ID (should be passed as UserId type)

    Returns:
        User information string
    """
    return f"User #{uid}"


# Create UserId values
user_id = UserId(12345)
print(fetch_user(user_id))  # Output: User #12345

# Note: UserId(1234) is still just 1234 at runtime, but type checkers
# treat UserId as distinct from int to prevent accidental type confusion

# ============================================================================
# 4. Generic Types - TypeVar
# ============================================================================
# Generic types are the most important part of advanced typing.
# TypeVar allows you to create a type variable that represents ANY type,
# helping you write flexible functions that work with multiple types.

T = TypeVar("T")  # T is a type variable representing any type


def first_item(lst: list[T]) -> T:
    """
    Get the first item from a list.
    The function preserves the type of list elements.

    Args:
        lst: A list of items of any type T

    Returns:
        The first item, which will be of the same type T as the list elements
    """
    return lst[0]


# Test with different types
int_list = [1, 2, 3]
str_list = ["a", "b", "c"]
float_list = [1.5, 2.5, 3.5]

result_int = first_item(int_list)
result_str = first_item(str_list)
result_float = first_item(float_list)

print(f"First int: {result_int}")  # Output: First int: 1
print(f"First str: {result_str}")  # Output: First str: a
print(f"First float: {result_float}")  # Output: First float: 1.5

# TypeVar allows the same function to work with any type while maintaining type safety


# ============================================================================
# 5. Core types in typing module
# ============================================================================

# --- 5.1 Any ---
# Any is the most permissive type. It's compatible with all types.
# Use it when you truly don't know or don't care about the type.


def process_any(x: Any) -> Any:
    """
    Process any type of input without type constraints.
    Type checkers won't report errors even if types don't match.
    """
    return x


print(process_any(42))  # Works with int
print(process_any("hello"))  # Works with string
print(process_any([1, 2, 3]))  # Works with list

# --- 5.2 Union - Accept multiple types ---
# Union allows a parameter to accept multiple specific types.


def process_union(x: Union[int, str]) -> Union[int, str]:
    """
    Accept either an integer or a string.
    If you pass a float, type checkers will report an error.
    """
    if isinstance(x, int):
        return x * 2
    else:
        return x.upper()


print(f"Union with int: {process_union(5)}")  # Output: Union with int: 10
print(f"Union with str: {process_union('hello')}")  # Output: Union with str: HELLO

# --- 5.3 Optional - Can be X or None ---
# Optional[X] is shorthand for Union[X, None].
# Use it for parameters/returns that might be None.


def process_optional(x: Optional[int]) -> Optional[str]:
    """
    Accept an integer that might be None.
    If None, return None; otherwise return a string representation.
    """
    if x is None:
        return None
    return f"The number is {x}"


print(process_optional(42))  # Output: The number is 42
print(process_optional(None))  # Output: None

# --- 5.4 Tuple - Fixed structure with multiple types ---
# Tuple specifies exact positions and types of elements.


def process_tuple(p: Tuple[int, str]) -> None:
    """
    Work with a tuple of exactly 2 elements: int and string.
    First position must be int, second must be string.
    """
    number, text = p
    print(f"Number: {number}, Text: {text}")


my_tuple: Tuple[int, str] = (5, "Hello")
process_tuple(my_tuple)  # Output: Number: 5, Text: Hello

# --- 5.5 Callable - Describe function types ---
# Callable specifies function signature: input types and return type.

from typing import Callable


def apply_operation(f: Callable[[int, int], int], a: int, b: int) -> int:
    """
    Apply a function to two integers.
    f must accept two ints and return an int.
    """
    return f(a, b)


# Example: pass a lambda or function that matches Callable[[int, int], int]
def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


print(f"Add 3 + 4: {apply_operation(add, 3, 4)}")  # Output: Add 3 + 4: 7
print(
    f"Multiply 3 * 4: {apply_operation(multiply, 3, 4)}"
)  # Output: Multiply 3 * 4: 12


# ============================================================================
# 6. Annotating Generators and Coroutines
# ============================================================================
# Generators use special type annotations to describe what they yield and return.

from typing import Generator


def count_up_to(max: int) -> Generator[int, None, None]:
    """
    Generate numbers from 0 to max-1.

    Generator[X, Y, Z] means:
    - X: Type of values yielded
    - Y: Type of values sent into the generator (None if not used)
    - Z: Type of the return value (None if not specified)
    """
    i = 0
    while i < max:
        yield i
        i += 1


# Test the generator
print("Numbers from generator:")
for num in count_up_to(5):
    print(num, end=" ")  # Output: 0 1 2 3 4
print()


# ============================================================================
# 7. Protocols - Structural Subtyping
# ============================================================================
# Protocols are like interfaces in other languages.
# A class doesn't need to inherit from Protocol to implement it;
# it just needs to have the required methods.

from typing import Protocol


class SupportsClose(Protocol):
    """
    Protocol defining objects that have a close() method.
    Any class with a close() method satisfies this protocol.
    """

    def close(self) -> None: ...


class FileWrapper:
    """
    A class that implements the SupportsClose protocol
    without explicitly inheriting from it.
    """

    def close(self) -> None:
        print("File closed!")


def close_resource(resource: SupportsClose) -> None:
    """
    Close any resource that has a close() method.
    Due to structural subtyping, FileWrapper works here.
    """
    resource.close()


# Structural subtyping: FileWrapper is treated as SupportsClose
file_obj = FileWrapper()
close_resource(file_obj)  # Output: File closed!


# ============================================================================
# 8. Deprecated Type Aliases (Old vs New Style)
# ============================================================================
# In Python 3.9+, you can use built-in types directly instead of typing module.
# The old typing.List, typing.Dict, etc. are deprecated.

# Old style (still works but deprecated):
# from typing import List, Dict
# def process(items: List[int]) -> Dict[str, int]:
#     pass


# Modern style (Python 3.9+):
def process_modern(items: list[int]) -> dict[str, int]:
    """
    Modern type hints using built-in types directly.
    No need to import from typing module for these basic types.
    """
    return {"count": len(items), "sum": sum(items)}


result = process_modern([1, 2, 3, 4, 5])
print(
    f"Processing result: {result}"
)  # Output: Processing result: {'count': 5, 'sum': 15}


# ============================================================================
# 9. Real-world Example - Small API
# ============================================================================
# Practical example: User database with type hints


def get_user_age(name: str) -> Optional[int]:
    """
    Retrieve a user's age from the database.

    Args:
        name: The name of the user to look up

    Returns:
        The user's age as an integer, or None if user not found
    """
    database = {"alice": 30, "bob": 25, "charlie": 35}
    return database.get(name)


# Test the function
print(f"Alice's age: {get_user_age('alice')}")  # Output: Alice's age: 30
print(f"Unknown age: {get_user_age('unknown')}")  # Output: Unknown age: None
