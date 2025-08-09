import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes, iterations: int = 390000) -> bytes:
    """
    Derive a 32-byte key from password+salt using PBKDF2-HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_data(data: bytes, key: bytes) -> tuple:
    """
    Encrypts data using AES-256-GCM.
    Returns: (nonce, ciphertext, tag)
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256-GCM")

    nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)
    return nonce, encrypted

def decrypt_data(nonce: bytes, encrypted: bytes, key: bytes) -> bytes:
    """
    Decrypts data using AES-256-GCM.
    """
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256-GCM")

    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted, None)