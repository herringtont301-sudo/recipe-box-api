from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(plain_password: str) -> str:
    """Return a secure hash for storing instead of the plain password."""
    return generate_password_hash(plain_password)

def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Return True if the candidate password matches the stored hash."""
    return check_password_hash(stored_hash, candidate_password)