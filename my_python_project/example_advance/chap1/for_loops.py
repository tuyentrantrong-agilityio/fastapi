# 1. Enumerate - Get both index and value
# ❌ WRONG - Manual index management, error-prone
i = 0
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"{i}: {fruit}")
    i += 1
# Output:
# 0: apple
# 1: banana
# 2: cherry


# ✅ CORRECT - Use enumerate
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# Output:
# 0: apple
# 1: banana
# 2: cherry

# Start from 1 instead of 0
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
# Output:
# 1. apple
# 2. banana
# 3. cherry


# 2. Loop through elements, not index
# ❌ WRONG - C/Java style, not Pythonic
i = 0
fruits = ["apple", "banana", "cherry"]
while i < len(fruits):
    print(fruits[i])
    i += 1


# ✅ CORRECT - Loop through each element
for fruit in fruits:
    print(fruit)

# Why:
# - Python cares about each element, not the index
# - Code is more concise and readable
# - No need to manage counter variable


# 3. For-else - Execute when loop completes normally (no break)
# ⭐ Rare but very useful

# Scenario: Check if any product in warehouse is broken
# ❌ WRONG - Use flag variable
products = [
    {"name": "phone", "broken": False},
    {"name": "laptop", "broken": False},
    {"name": "tablet", "broken": False},
]

found_broken = False
for product in products:
    if product["broken"]:
        print(f"❌ Found broken product: {product['name']}")
        found_broken = True
        break

if not found_broken:
    print("✅ All products are okay")


# ✅ CORRECT - Use for-else
for product in products:
    if product["broken"]:
        print(f"❌ Found broken product: {product['name']}")
        break
else:
    # else only runs when loop completes normally (no break)
    print("✅ All products are okay")


# Another example: Find odd number
numbers = [2, 4, 6, 8, 10]
for num in numbers:
    if num % 2 != 0:  # Find odd number
        print(f"Found odd number: {num}")
        break
else:
    print("No odd numbers")


# 📝 Remember:
# for-else is a Pythonic way to:
# - Execute code when loop completes without break
# - Instead of using flag variable
# - Make code clear and readable
