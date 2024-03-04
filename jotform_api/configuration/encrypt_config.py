from cryptography.fernet import Fernet
import json

# This is a one-time script to encrypt the configuration data and save it to a file.
# Fill in the configuration data and run this script to generate the encrypted configuration file.

# Generate a key and save it somewhere secure
key = Fernet.generate_key()
cipher_suite = Fernet(key)
with open("jotform_api/api_endpoints/encryption_key.key", "wb") as key_file:
    key_file.write(key)

# Your configuration data
config_data = {
    "JOTFORM_API_KEY": "your_api_key_here", 
    "JOTFORM_LTJJC_INDUCTION_FORM_ID": "your_form_id_here"
}

# Convert your configuration data to JSON and encrypt it
config_json = json.dumps(config_data).encode()
cipher_text = cipher_suite.encrypt(config_json)

# Save the encrypted configuration to a file
with open("jotform_api/api_endpoints/encrypted_config_file.enc", "wb") as encrypted_file:
    encrypted_file.write(cipher_text)

print("Configuration encrypted and saved.")
