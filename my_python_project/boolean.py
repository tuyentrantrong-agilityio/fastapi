# ============================================================================
# BOOLEAN VALUES IN PYTHON
# ============================================================================
# Booleans are data types that can only have two values: True or False
# They are commonly used in conditions and logical operations

print("=" * 70)
print("1. BASIC BOOLEAN VALUES")
print("=" * 70)
print()

# The two boolean values in Python
is_raining = True
is_snowing = False

print(f"is_raining = {is_raining}")
print(f"is_snowing = {is_snowing}")
print()

# Check the data type
print(f"Type of True: {type(True)}")
print(f"Type of False: {type(False)}")
print()

# ============================================================================
print("=" * 70)
print("2. COMPARISON OPERATORS (Return Boolean Values)")
print("=" * 70)
print()

# Equal to (==)
print("--- Equal To (==) ---")
print(f"5 == 5: {5 == 5}")  # True
print(f"5 == 3: {5 == 3}")  # False
print(f"'hello' == 'hello': {'hello' == 'hello'}")  # True
print()

# Not equal to (!=)
print("--- Not Equal To (!=) ---")
print(f"5 != 3: {5 != 3}")  # True
print(f"5 != 5: {5 != 5}")  # False
print()

# Greater than (>)
print("--- Greater Than (>) ---")
print(f"10 > 5: {10 > 5}")  # True
print(f"3 > 7: {3 > 7}")  # False
print()

# Less than (<)
print("--- Less Than (<) ---")
print(f"3 < 7: {3 < 7}")  # True
print(f"10 < 5: {10 < 5}")  # False
print()

# Greater than or equal to (>=)
print("--- Greater Than or Equal To (>=) ---")
print(f"5 >= 5: {5 >= 5}")  # True
print(f"5 >= 3: {5 >= 3}")  # True
print(f"3 >= 5: {3 >= 5}")  # False
print()

# Less than or equal to (<=)
print("--- Less Than or Equal To (<=) ---")
print(f"5 <= 5: {5 <= 5}")  # True
print(f"3 <= 5: {3 <= 5}")  # True
print(f"5 <= 3: {5 <= 3}")  # False
print()

# ============================================================================
print("=" * 70)
print("3. LOGICAL OPERATORS: and, or, not")
print("=" * 70)
print()

# AND operator: both conditions must be True
print("--- AND Operator: and ---")
age = 25
has_license = True

print(f"age = {age}, has_license = {has_license}")
print(f"age >= 18 and has_license: {age >= 18 and has_license}")  # True
print()

age = 15
print(f"age = {age}, has_license = {has_license}")
print(f"age >= 18 and has_license: {age >= 18 and has_license}")  # False
print()

# Practical example: Can rent a car?
age = 25
has_credit_card = True
is_employed = True

can_rent_car = age >= 21 and has_credit_card and is_employed
print(
    f"Can rent car (age {age}, card: {has_credit_card}, employed: {is_employed}): {can_rent_car}"
)
print()

# OR operator: at least one condition must be True
print("--- OR Operator: or ---")
has_phone = False
has_laptop = True

print(f"has_phone = {has_phone}, has_laptop = {has_laptop}")
print(f"has_phone or has_laptop: {has_phone or has_laptop}")  # True
print()

# Practical example: Can attend meeting?
has_computer = False
has_phone = True
print(
    f"Can attend meeting (computer: {has_computer}, phone: {has_phone}): {has_computer or has_phone}"
)
print()

# NOT operator: reverses the boolean value
print("--- NOT Operator: not ---")
is_sunny = True
print(f"is_sunny = {is_sunny}")
print(f"not is_sunny: {not is_sunny}")  # False
print()

is_raining = False
print(f"is_raining = {is_raining}")
print(f"not is_raining: {not is_raining}")  # True
print()

# ============================================================================
print("=" * 70)
print("4. TRUTH TABLE: and, or, not")
print("=" * 70)
print()

# AND Truth Table
print("--- AND Truth Table ---")
print("A     | B     | A and B")
print("------|-------|--------")
print("True  | True  |", True and True)
print("True  | False |", True and False)
print("False | True  |", False and True)
print("False | False |", False and False)
print()

# OR Truth Table
print("--- OR Truth Table ---")
print("A     | B     | A or B")
print("------|-------|-------")
print("True  | True  |", True or True)
print("True  | False |", True or False)
print("False | True  |", False or True)
print("False | False |", False or False)
print()

# NOT Truth Table
print("--- NOT Truth Table ---")
print("A     | not A")
print("------|------")
print("True  |", not True)
print("False |", not False)
print()

# ============================================================================
print("=" * 70)
print("5. IF STATEMENTS WITH BOOLEAN CONDITIONS")
print("=" * 70)
print()

# Simple if statement
age = 18
if age >= 18:
    print(f"Age {age}: You are an adult")
else:
    print(f"Age {age}: You are a minor")
print()

# If-elif-else
score = 75
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Score {score}: Grade {grade}")
print()

# Multiple conditions with and/or
password = "SecurePass123"
password_length = len(password)
has_numbers = any(char.isdigit() for char in password)
has_uppercase = any(char.isupper() for char in password)

is_strong_password = password_length >= 8 and has_numbers and has_uppercase
print(f"Password: {password}")
print(f"Length >= 8: {password_length >= 8}")
print(f"Has numbers: {has_numbers}")
print(f"Has uppercase: {has_uppercase}")
print(f"Is strong password: {is_strong_password}")
print()

# ============================================================================
print("=" * 70)
print("6. PRACTICAL EXAMPLES: REAL-WORLD USE CASES")
print("=" * 70)
print()

# Example 1: Login validation
print("--- Login Validation ---")
username = "john_doe"
password = "secure123"
is_username_correct = username == "john_doe"
is_password_correct = password == "secure123"

is_login_valid = is_username_correct and is_password_correct
print(f"Username correct: {is_username_correct}")
print(f"Password correct: {is_password_correct}")
print(f"Login valid: {is_login_valid}")
print()

# Example 2: Weather check
print("--- Weather Check ---")
temperature = 28  # Celsius
is_sunny = True
is_humid = True

is_good_weather = temperature > 20 and temperature < 35 and is_sunny
is_bad_weather = temperature < 0 or temperature > 40 or not is_sunny

print(f"Temperature: {temperature}°C")
print(f"Is sunny: {is_sunny}")
print(f"Is good weather (20-35°C and sunny): {is_good_weather}")
print(f"Is bad weather (extreme temp or not sunny): {is_bad_weather}")
print()

# Example 3: Product eligibility
print("--- Product Eligibility Check ---")
user_age = 21
is_verified = True
has_payment_method = True

is_eligible = user_age >= 18 and is_verified and has_payment_method
print(f"Age: {user_age}, Verified: {is_verified}, Payment method: {has_payment_method}")
print(f"Eligible to purchase: {is_eligible}")
print()

# ============================================================================
print("=" * 70)
print("7. BOOLEAN CONVERSION: TRUTHY AND FALSY VALUES")
print("=" * 70)
print()

# Values that are considered False (falsy)
print("--- Falsy Values ---")
print(f"bool(0): {bool(0)}")  # False
print(f"bool(''): {bool('')}")  # False (empty string)
print(f"bool([]): {bool([])}")  # False (empty list)
print(f"bool(None): {bool(None)}")  # False
print()

# Values that are considered True (truthy)
print("--- Truthy Values ---")
print(f"bool(1): {bool(1)}")  # True
print(f"bool('hello'): {bool('hello')}")  # True
print(f"bool([1, 2, 3]): {bool([1, 2, 3])}")  # True (non-empty list)
print()

# Using truthy/falsy in conditions
print("--- Using Truthy/Falsy in Conditions ---")
user_input = ""
if user_input:
    print("User entered something")
else:
    print("User entered nothing (empty string is falsy)")
print()

items = [1, 2, 3]
if items:
    print(f"You have items: {items}")
else:
    print("No items")
print()

# ============================================================================
print("=" * 70)
print("8. COMBINING MULTIPLE COMPARISONS")
print("=" * 70)
print()

# Check if a number is in a range
number = 15
print(f"Number: {number}")
print(f"0 < number < 20: {0 < number < 20}")  # True
print(f"10 <= number <= 20: {10 <= number <= 20}")  # True
print()

# Check multiple conditions
student_score = 85
attendance = 95
behavior = "good"

passes_exam = student_score >= 60
has_good_attendance = attendance >= 80
has_good_behavior = behavior == "good"

is_model_student = passes_exam and has_good_attendance and has_good_behavior
print(f"Score: {student_score}, Attendance: {attendance}%, Behavior: {behavior}")
print(f"Passes exam: {passes_exam}")
print(f"Good attendance: {has_good_attendance}")
print(f"Good behavior: {has_good_behavior}")
print(f"Is model student: {is_model_student}")
print()

# ============================================================================
print("=" * 70)
print("9. USING BOOLEAN VALUES IN LISTS AND LOOPS")
print("=" * 70)
print()

# List of boolean values
features = [True, False, True, True, False]
print(f"Features enabled: {features}")
print(f"Number of enabled features: {sum(features)}")
print(f"All features enabled: {all(features)}")
print(f"At least one feature enabled: {any(features)}")
print()

# Loop with boolean conditions
print("--- Checking numbers 1-10 ---")
for num in range(1, 11):
    is_even = num % 2 == 0
    is_greater_than_5 = num > 5

    if is_even and is_greater_than_5:
        print(f"{num}: Even and greater than 5 ✓")
    elif is_even:
        print(f"{num}: Even only")
    elif is_greater_than_5:
        print(f"{num}: Greater than 5 only")
print()

print("=" * 70)
print("BOOLEAN SUMMARY")
print("=" * 70)
print("• Booleans have only two values: True and False")
print("• Comparison operators (==, !=, <, >, <=, >=) return booleans")
print("• Logical operators (and, or, not) combine boolean values")
print("• Use booleans in if/else statements for decision making")
print("• Truthy values (non-zero, non-empty) evaluate to True")
print("• Falsy values (0, '', [], None) evaluate to False")
print("=" * 70)
