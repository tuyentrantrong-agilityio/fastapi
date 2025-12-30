# ===== VARIABLE SCOPE - GLOBAL VS LOCAL =====

kteam = "How Kteam"  # Global variable


def say_slogan():
    """Function with local variable shadowing global"""
    kteam = "Kteam"  # Local variable (does not affect global)
    print(f"{kteam} is the best")


say_slogan()  # Output: "Kteam is the best"
print(kteam)  # Output: "How Kteam" (global unchanged)


# ===== MUTABLE VS IMMUTABLE ARGUMENTS =====

num = 69  # Immutable (int)
st = "How much"  # Immutable (string)
lst = [1, 2, 3]  # Mutable (list)
tup = tuple("Education")  # Immutable (tuple)


def change(params):
    """Modify mutable objects passed as arguments"""
    # Note: Reassigning params would only change local reference
    # params = 420  # This only changes local variable, not original
    params[1] = "New value"  # This modifies the mutable object itself
    print("Change successfully")


# change(num)  # Will not work - int is immutable
# change(st)  # Will not work - string is immutable

change(lst)  # Works - list is mutable and gets modified
print(lst)  # Output: [1, 'New value', 3]

# change(tup)  # Will not work - tuple is immutable
print(num, st, lst, tup)


# ===== MODIFYING GLOBAL VARIABLES =====


def make_slogan():
    """Use global keyword to modify global variable from within function"""
    global kteam  # Declare intention to modify global variable
    kteam = "Kteam"  # Now this modifies the global variable, not local
    print(f"{kteam} is the best")


make_slogan()  # Execute function to modify global variable
print(kteam)  # Output: "Kteam" (global was successfully modified)
