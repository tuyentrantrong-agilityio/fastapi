# ============================================================================
# PRINT FUNCTION IN PYTHON
# ============================================================================

# BASIC PRINT: CONCATENATION WITH PLUS (+) VS COMMA (,)

# Using comma (,) is the easiest way to print multiple items
# Python automatically adds spaces between them
print("hello", "world", "python", 69)

# Using plus (+) requires all items to be strings (same data type)
# This causes an error because 69 is an integer, not a string:
# print("hello" + " " + "world" + " " + "python" + 69)  # TypeError!

# To fix it, convert the number to a string:
print("hello" + " " + "world" + " " + "python" + str(69))

# THE 'sep' PARAMETER: CHANGE SEPARATOR BETWEEN ITEMS

# Default separator is a space
print("apple", "banana", "cherry")

# Change separator to a dash
print("hello", "world", "python", 69, sep="-")

# Change separator to pipe (useful for CSV-like output)
print("apple", "banana", "cherry", sep=" | ")

# Change separator to empty string (no space between items)
print("a", "b", "c", sep="")

# Practical example: Creating a formatted date
print(2025, 12, 25, sep="-")  # Output: 2025-12-25

# Practical example: Creating a path
print("home", "user", "documents", sep="/")  # Output: home/user/documents

# THE 'end' PARAMETER: CHANGE WHAT PRINTS AT THE END (default is newline)

# Change end to exclamation mark
print("hello", "world", "python", 69, end="!")
print()  # Print newline separately

# Change end to double asterisks
print("Python", "is", "awesome", end="***")
print()

# No end character (continues on same line)
print("A", end="")
print("B", end="")
print("C")


# WORKING WITH TIME: PAUSE PROGRAM EXECUTION
from time import sleep  # Import the sleep function from the time module

print("Program starting...")
sleep(2)  # Pause execution for 2 seconds
print("2 seconds have passed!")


# WRITING PRINT OUTPUT TO A FILE
# Using the file parameter to save print output to a file instead of screen
with open("output.txt", "w") as f:
    print("This line goes to the file", file=f)
    print("This is the second line", file=f)

# THE 'flush' PARAMETER: FORCE OUTPUT IMMEDIATELY
# flush=True forces immediate output (useful for progress indicators)
print("hello", "world", "python", 69, flush=True)


# INPUT FUNCTION: GET DATA FROM USER
# input() displays a prompt message and waits for user input
example_input = input("Enter your name: ")
print("You entered:", example_input)

# Important: input() always returns a STRING, even if you type a number
age_string = input("Enter your age: ")
print("You entered:", age_string, "Type:", type(age_string))

# To use input as a number, convert it explicitly:
# age_number = int(input("Enter your age: "))

# FORMATTED OUTPUT WITH %-FORMATTING
name = "Alice"
age = 28
city = "Tokyo"

# Using % formatting to insert values into strings
print("My name is %s" % name)
print("I am %d years old" % age)  # %d for integers
print("I live in %s" % city)

# Multiple values with % formatting
print("Name: %s, Age: %d, City: %s" % (name, age, city))

# %r shows the value with quotes (raw representation)
value = "Hello"
print("String representation: %r" % value)

# EMPTY INPUT: PRESSING ENTER WITH NO TEXT
# If user presses Enter without typing anything, input returns an empty string
empty = input("Press Enter without typing anything: ")
print("Length of input:", len(empty))  # Length will be 0
if empty == "":
    print("You entered nothing (empty string)")
# WARNING: THE DANGEROUS eval() FUNCTION
# eval() executes Python code from a string - VERY RISKY with untrusted input
result = eval("1 + 1")
print("eval('1 + 1') =", result)

result = eval("10 * 5")
print("eval('10 * 5') =", result)

# DANGER: eval() can execute ANY Python code!
# Example of why it's dangerous:
# eval("__import__('os').system('rm -rf *')")  # Could delete files!
# Never use eval() with user input!
