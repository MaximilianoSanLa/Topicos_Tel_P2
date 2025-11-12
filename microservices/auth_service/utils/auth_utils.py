from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(stored_password: str, input_password: str) -> bool:
    return check_password_hash(stored_password, input_password)
