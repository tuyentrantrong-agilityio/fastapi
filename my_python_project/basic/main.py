def main():
    """Main entry point of the program."""
    print("Hello from my-python-project!")


if __name__ == "__main__":
    main()

# ===== 1. Basic Loop Examples =====
print("\n--- 1. For Loop Example ---")
name = "tuyen"
for i in range(5):
    print(f"{name} {i}")

# ===== 2. Boolean Logic =====
print("\n--- 2. Boolean Logic ---")
a = not True  # not True = False
if a:
    print("a is true")
else:
    print("a is false")

# Comparison
print(f"42 == 42: {42 == 42}")

# ===== 3. While Loop Example =====
print("\n--- 3. While Loop Example ---")
spam = 0
while spam < 5:
    print(f"I learn Python: {spam}")
    spam += 1

# ===== 4. String Operations =====
print("\n--- 4. String Operations ---")
text = "hello world\nthis is a long string\nthat spans multiple lines"
repeat_text = text * 2  # Repeat string 2 times
print(f"Original text:\n{text}")
print(f"\nLength: {len(text)}")

# ===== 5. Turtle Graphics Example (commented out) =====
# from turtle import penup, pendown, forward
#
# def jump(length):
#     """Move forward length units without leaving a trail.
#
#     Postcondition: Leaves the pen down.
#     """
#     penup()
#     forward(length)
#     pendown()

# ===== 6. Random Numbers =====
print("\n--- 6. Random Numbers ---")
import random

random_num = random.randint(1, 46)
print(f"Random number between 1-46: {random_num}")

# ===== 7. Functions with Parameters =====
print("\n--- 7. Functions with Parameters ---")


def display_info(text, age):
    """Display text and age information."""
    print(f"Text: {text}")
    print(f"Age: {age}")


# Calling function with different arguments
display_info("hello", 86)
display_info("world", 96)
display_info("vietnam", 36)

# ===== 8. Default Parameters =====
print("\n--- 8. Default Parameters ---")


def display_info_with_defaults(text, age=0, success=False):
    """Display info with default parameter values."""
    print(f"Text: {text}")
    print(f"Age: {age}")
    print(f"Success: {success}")


display_info_with_defaults("parameter defaults", 861)

# ===== 9. String Methods =====
print("\n--- 9. String Methods ---")
original = "how method of string works"

print(f"Original: {original}")
print(f"title(): {original.title()}")
print(f"upper(): {original.upper()}")
print(f"center(50, '-'): {original.center(50, '-')}")
print(f"ljust(50, '-'): {original.ljust(50, '-')}")
print(f"rjust(50, '-'): {original.rjust(50, '-')}")

# ===== 10. String Encoding and Joining =====
print("\n--- 10. String Encoding & Joining ---")
text_unicode = "Python"
encoded = text_unicode.encode("utf-8")
print(f"Encoded: {encoded}")

joined = ", ".join(["apple", "banana", "cherry"])
print(f"Joined: {joined}")

# ===== 11. String Splitting and Partitioning =====
print("\n--- 11. Splitting & Partitioning ---")
text_split = "how method of string works"
split_result = text_split.split(" ")
print(f"Split by space: {split_result}")

partition_result = text_split.partition(" ")
print(f"Partition: {partition_result}")

rpartition_result = text_split.rpartition(" ")
print(f"Right partition: {rpartition_result}")

# ===== 12. String Searching Methods =====
print("\n--- 12. String Searching ---")
text_search = "how method of string works"
print(f"Count 'o': {text_search.count('o')}")
print(f"Count 'o' (0-10): {text_search.count('o', 0, 10)}")
print(f"Starts with 'how': {text_search.startswith('how')}")
print(f"Find 't': {text_search.find('t')}")
# Note: find() returns -1 if not found, index() raises error if not found

# ===== 13. String Trimming =====
print("\n--- 13. String Trimming ---")
text_spaces = "  hello world  "
print(f"strip(): '{text_spaces.strip()}'")
print(f"lstrip(): '{text_spaces.lstrip()}'")
print(f"rstrip(): '{text_spaces.rstrip()}'")
