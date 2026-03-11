from passlib.context import CryptContext

# Use argon2id for better security (no length limitations like bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password using argon2id.

    Argon2id is more secure than bcrypt and has no length limitations.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password using argon2id.
    """
    return pwd_context.verify(plain_password, hashed_password)
