# Create a generator expression that yields numbers from 0 to 2
length = 3
iter = (x for x in range(length))  # Generator object created
# Iterate through the generator and print each value
for i in iter:
    print(i)

# While loop to consume remaining values from the generator using next()
while 1:
    try:
        print(next(iter))  # Get the next value from the generator
    except StopIteration:  # Catch exception when generator is exhausted
        break  # Exit the while loop
# Tuple unpacking in a for loop - unpack pairs of values
for variable_1, variable_2 in [(1, 2), (3, 4), (5, 6)]:
    print(variable_1, variable_2)


# Create a generator and iterate through it
iter1 = (x for x in range(3))
for i in iter1:
    print(i)

# Iterate through dictionary items and unpack key-value pairs
iter2 = {"name": "Tuyen", "age": 36}
for key, value in iter2.items():
    print(key, value)
    if key == "name":  # Break when key is "name"
        break


# Iterate through a string and break when a space is found
s = "How Tuyen"
for key in s:
    if key == " ":  # Check if current character is a space
        break
    else:
        print(key)


# For-else clause: else block executes if loop completes without break
for k in (1, 2, 3):
    print(k)
else:
    print("Done")
# Note: Using break exits the loop completely and skips the else block
# Note: Using continue skips the current iteration but continues to the next one

# Calculate the sum of all elements in a set
tong = 0  # Initialize sum variable

set_ = {5, 8, 1, 9, 4}  # Create a set of integers
for i in set_:  # Iterate through each element in the set
    tong = tong + i  # Add current element to the sum
print(tong)  # Print the total sum
