import bcrypt
import secrets


def generate_password() -> str:
    return secrets.token_urlsafe(10)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
