# 1. Early Return - Exit early when encountering errors
# ⚠️ Problem: Too deep if nesting, hard to read

# ❌ WRONG - Deep if nesting, main logic is buried
def process_login_bad(username, password, is_admin=False):
    if username:
        if password:
            if is_admin:
                print("Processing admin...")
                return True
            else:
                return False
        else:
            return False
    else:
        return False


# ✅ CORRECT - Exit early, main logic at the end
def process_login(username, password, is_admin=False):
    # Check each condition if wrong -> exit immediately
    if not username:
        print("Error: username is empty")
        return False

    if not password:
        print("Error: password is empty")
        return False

    if not is_admin:
        print("Error: not an admin")
        return False

    # Main logic - easy to read, aligned
    print("Admin processing successful")
    return True


print(process_login("tuyen", "pass123", is_admin=True))


# 2. Comparison chaining - Check if value is within range
# ❌ WRONG - Verbose
age = 25
if age >= 18 and age <= 65:
    print("Age is valid")


# ✅ CORRECT - Chaining comparison (Pythonic)
if 18 <= age <= 65:
    print("Age is valid")


# 3. Do not write code on the same line as the colon
# ❌ WRONG - Hard to expand, easy to misread
name = "Tuyen"
if name:
    print("Hello", name)


# ✅ CORRECT - Write code on separate line
if name:
    print("Hello", name)


# 4. Check if value is in a list
# ❌ WRONG - Variable repetition, verbose, easy to type wrong
team_lead = "Tuyen"
if team_lead == "Tuyen" or team_lead == "Sinh" or team_lead == "Huyen":
    print("This is a team lead")


# ✅ CORRECT - Use 'in' with list
if team_lead in ["Tuyen", "Sinh", "Huyen"]:
    print("This is a team lead")

# Or use tuple (slightly faster than list)
if team_lead in ("Tuyen", "Sinh", "Huyen"):
    print("This is a team lead")


# 5. Truthiness - Check if value is true/false
# Python considers these values as False:
# None, 0, 0.0, '', [], {}, (), False

# ❌ WRONG - Verbose
foo = "hello"
if foo == True:
    print("foo is true")


# ✅ CORRECT - Use truthiness directly
if foo:
    print("foo has a value")


# ⭐ Special case: Check for None
position = None
if position:  # ❌ WRONG - If position is 0, result is wrong
    print(f"Position: {position}")

if position is not None:  # ✅ CORRECT - Check None explicitly
    print(f"Position: {position}")


# 6. Ternary operator - Quick assignment with if-else
# ❌ WRONG - 4 lines for one assignment
is_active = True
status = ""
if is_active:
    status = "Active"
else:
    status = "Inactive"


# ✅ CORRECT - 1 line with ternary operator
status = "Active" if is_active else "Inactive"
print(status)
