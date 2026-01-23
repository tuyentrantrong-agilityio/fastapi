# 1. Exception - Handle errors explicitly
# ⚠️ Problem: Check before doing

user_data = {"username": "tuyen"}

# ❌ WRONG - Sequential check is prone to race condition
if "email" in user_data:
    email = user_data["email"]
    print(f"Email: {email}")
else:
    print("Email not found")


# ✅ CORRECT - Use try-except to catch errors
def get_email(data):
    try:
        return data["email"]
    except KeyError:
        return None


email = get_email(user_data)
print(f"Email: {email}")  # Email: None


# 2. Should not "swallow" exceptions without handling
# ❌ WRONG - Exception is ignored, hard to debug
def fetch_data_bad():
    try:
        # code that might fail
        pass
    except:
        print("Oops")  # What error?


# ✅ CORRECT - Handle or re-raise exception
def fetch_data_good():
    try:
        # code that might fail
        pass
    except ConnectionError as e:
        print(f"Connection error: {e}")
        raise  # Re-raise if cannot handle
    except ValueError as e:
        print(f"Invalid data: {e}")


# 3. Define custom exceptions
# ⭐ Benefits: Clear API, easy to catch right error type


class URLFetchError(Exception):
    """Exception when unable to fetch URL"""

    pass


class InvalidCredentialsError(Exception):
    """Exception when login credentials are incorrect"""

    pass


def login(username, password):
    if not username or not password:
        raise InvalidCredentialsError("Username and password cannot be empty")
    print(f"Successfully logged in with user: {username}")


# Usage
try:
    login("", "password")
except InvalidCredentialsError as e:
    print(f"Login error: {e}")
# When elements are exhausted:
# Python throws StopIteration
# for loop catches it
# and stops
# you use exception without knowing

# if key in dict
#    if dict[key]:
# problem:
# check is never enough
# prone to race condition
# code is messy

# should write
# try:
#     return dict['key']
# except KeyError:
#     return None

# just do it and catch error if it fails

# should not swallow specific exceptions
# except:
#     print('Oops')

# if cannot handle -> re-raise
# except:
#    log()
#    raise

# define custom exception
# raise RuntimeError("Something wrong")
# problem: user cannot distinguish where error comes from

# correct way to write


class URLFetchError(Exception):
    pass


raise URLFetchError("Fetch failed")
# benefits
# catch right error
# code is clear
# API is clean
