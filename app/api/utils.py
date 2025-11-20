import secrets


def generate_password() -> str:
    return secrets.token_urlsafe(10)
