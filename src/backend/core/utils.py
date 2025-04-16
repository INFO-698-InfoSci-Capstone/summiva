import secrets

def generate_secure_token():
    return secrets.token_urlsafe(32)