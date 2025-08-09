import getpass
from typing import Tuple
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derive a 32-byte key from password and salt using PBKDF2.
    """
    if not salt or len(salt) < 8:
        raise ValueError("Invalid salt provided for key derivation.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

def prompt_password_and_derive(salt: bytes) -> bytes:
    """
    Prompts user for password and returns derived key.
    """
    # Use getpass so password isn't echoed
    pwd = getpass.getpass("Enter password to unlock this capsule: ")
    return derive_key_from_password(pwd, salt)
