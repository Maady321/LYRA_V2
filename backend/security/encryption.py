import os
from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
from backend.core.config import settings, BASE_DIR

# Key management: Generate or load master key
_ENCRYPTION_KEY_PATH = os.path.join(BASE_DIR, ".env.key")

def _get_or_create_key() -> bytes:
    if os.path.exists(_ENCRYPTION_KEY_PATH):
        with open(_ENCRYPTION_KEY_PATH, "rb") as f:
            return f.read().strip()
    else:
        key = Fernet.generate_key()
        with open(_ENCRYPTION_KEY_PATH, "wb") as f:
            f.write(key)
        return key

MASTER_KEY = _get_or_create_key()
_fernet = Fernet(MASTER_KEY)

def encrypt_value(value: str) -> str:
    if value is None:
        return None
    return _fernet.encrypt(value.encode('utf-8')).decode('utf-8')

def decrypt_value(value: str) -> str:
    if value is None:
        return None
    try:
        return _fernet.decrypt(value.encode('utf-8')).decode('utf-8')
    except Exception:
        # Fallback for unencrypted legacy data during migration
        return value

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy custom type that transparently encrypts data on write
    and decrypts it on read.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_value(str(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_value(str(value))
        return value
