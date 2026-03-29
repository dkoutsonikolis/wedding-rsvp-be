import hashlib

from config import settings


def hash_session_token(plaintext: str) -> str:
    pepper = settings.ANONYMOUS_AGENT_TOKEN_PEPPER
    payload = f"{pepper}\0{plaintext}".encode()
    return hashlib.sha256(payload).hexdigest()
