# ===== IF/ELSE - Conditional Branching =====
# if statements allow code to make decisions based on conditions
# Syntax: if condition: do this, else: do that

# Example 1: Basic if-else
print("--- Example 1: Basic if-else ---")
a = 0
b = 3
if a >= 0:
    print("a >= 0")
    if a < b:
        print("a < b")
else:
    print("a < 0")

# Example 2: if-elif-else
print("\n--- Example 2: if-elif-else ---")
score = 75
if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
else:
    print("Grade: F")

# Example 3: Multiple conditions with and/or
print("\n--- Example 3: Multiple conditions ---")
age = 25
has_license = True
if age >= 18 and has_license:
    print("You can drive!")
else:
    print("You cannot drive")

# Example 4: Not operator
print("\n--- Example 4: Using NOT operator ---")
is_raining = False
if not is_raining:
    print("It's a nice day, let's go outside!")

# ===== WHILE LOOPS - Repeat until condition is false =====
# while loops continue executing as long as the condition is True

# Example 1: Basic while loop
print("\n--- Example 1: Basic while loop ---")
a = 0
b = 3
while a < b:
    print(f"a = {a}, still less than b")
    a += 1

# Example 2: String iteration with while
print("\n--- Example 2: String iteration with while ---")
s = "hello"
print("Removing characters one by one:")
while s:
    print(s)
    s = s[1:]  # Remove first character each iteration

# Example 3: Using break and continue
print("\n--- Example 3: break and continue ---")
# break: exits the loop immediately
# continue: skips to the next iteration


# Example 4: Infinite loop with break (original infinite loop approach)
print("\n--- Example 4: Infinite loop with break ---")
# while True creates an infinite loop - we need a break condition to exit
# Method 1 (commented): Using infinite loop
# five_even_numbers = []
# k_number = 1
# while True:  # infinite loop (dangerous without break)
#     if k_number % 2 == 0:  # if k_number is even
#         five_even_numbers.append(k_number)  # add to list
#     if len(five_even_numbers) == 5:  # if we have 5 even numbers
#         break  # exit the loop
#     k_number += 1
# Result: [2, 4, 6, 8, 10]

# Example 5: Better approach - Find first 5 even numbers
print("--- Example 5: Find first 5 even numbers (improved) ---")
five_even_numbers = []
k_number = 1

# While there are less than 5 even numbers, keep searching
while len(five_even_numbers) < 5:
    if k_number % 2 != 0:  # If odd number, skip to next
        k_number += 1
        continue  # continue: skip rest of loop, go to next iteration
    five_even_numbers.append(k_number)  # Add even number to list
    k_number += 1

print(f"First 5 even numbers: {five_even_numbers}")
print(f"Final k_number value: {k_number}")

# ===== EXERCISE 1: File Processing with String Replacement =====
print("\n--- Exercise 1: File processing with string replacement ---")
# Read from draft.txt, replace "Kteam" with "How", write to tuyen.txt
try:
    with open("draft.txt", "r") as f:
        with open("tuyen.txt", "w") as t:
            for line in f:
                words = line.split()  # Split line into words
                for i in range(len(words)):
                    if words[i] == "Kteam":  # Find "Kteam"
                        if i > 0:  # Make sure there's a word before it
                            words[i - 1] = "How"  # Replace previous word
                new_line = " ".join(words)  # Join words back to line
                t.write(new_line + "\n")  # Write to file
    print("File processing complete!")
except FileNotFoundError:
    print("Note: draft.txt file not found. Skipping this exercise.")


# ===== EXERCISE 2: Sort array while keeping certain values in place =====
print("--- Exercise 2: Sort array excluding specific value ---")
# Goal: Sort array but keep all occurrences of 11 in their original positions

array = [56, 14, 11, 756, 34, 90, 11, 11, 65, 0, 11, 35]
print(f"Original array: {array}")

array_sorted_values = []  # Store non-11 values
j = 0

# Extract all non-11 values and sort them
for i in range(len(array)):
    if array[i] != 11:
        array_sorted_values.append(array[i])

array_sorted_values.sort()  # Sort the extracted values
print(f"Sorted non-11 values: {array_sorted_values}")

# Put sorted values back, keeping 11s in place
for i in range(len(array)):
    if array[i] != 11:
        array[i] = array_sorted_values[j]
        j += 1

print(f"Final array (11s preserved): {array}")
print(f"Note: All 11s are in original positions, other values are sorted")
