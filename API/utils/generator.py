from cryptography.fernet import Fernet
import secrets 
import base64
import json

def generate_key(key_size=32):
    """Generates a random cryptographic key of the specified size in bytes."""
    key = secrets.token_bytes(key_size)  # Generates random bytes
    encoded_key = base64.urlsafe_b64encode(key).decode('utf-8')
    return encoded_key

def encrypt_data(fernet: Fernet, data: dict):
    """ Encrypts the data in json format using the fernet instance """
    encrypted_data = fernet.encrypt(json.dumps(data, indent=4).encode())
    print(encrypted_data)
    return encrypted_data.decode()

def decrypt_data(fernet: Fernet, data):
    """ Decrypts the data in json format using the fernet instance """
    decrypted_data = json.loads(fernet.decrypt(data).decode())
    return decrypted_data

def create_fernet_instance(key: str):
    return Fernet(key)
