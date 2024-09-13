import secrets
secret_key = secrets.token_hex(32)  # Generates a 64-character hexadecimal string
print(secret_key)
