from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


def base_encryption(password):
    password = bytes(password, 'utf-8')
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=password, iterations=100000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f


def encrypt(data, password):
    # Todo: force good password?
    """Encrypts data using the password"""
    f = base_encryption(password)
    token = f.encrypt(bytes(data, 'utf-8'))
    return token.decode()


def decrypt(data, password):
    """Decrypts data using the password"""
    f = base_encryption(password)
    token = f.decrypt(bytes(data, 'utf-8'))
    return token.decode()
