import secrets

# Generate a secure random string (hexadecimal)
SECRET_KEY = secrets.token_hex(24)

print (SECRET_KEY)