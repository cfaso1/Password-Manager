import os, base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

SALT_FILE = "salt.bin"

def load_or_create_salt():
    if not os.path.exists(SALT_FILE):
        with open(SALT_FILE, "wb") as f:
            f.write(os.urandom(16))
    with open(SALT_FILE, "rb") as f:
        return f.read()
    
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def encrypt(text: str, key: bytes) -> str:
    return Fernet(key).encrypt(text.encode()).decode()

def decrypt(token: str, key: bytes) -> str:
    return Fernet(key).decrypt(token.encode()).decode()