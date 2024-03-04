from cryptography.fernet import Fernet
import json

def load_encrypted_config(key_path, config_path):
    # Load the encryption key
    with open(key_path, "rb") as key_file:
        key = key_file.read()

    cipher_suite = Fernet(key)

    # Decrypt the configuration file
    with open(config_path, "rb") as encrypted_file:
        cipher_text = encrypted_file.read()
        decrypted_json = cipher_suite.decrypt(cipher_text)

    # Convert JSON string back to a Python dictionary
    config_data = json.loads(decrypted_json.decode())

    return config_data