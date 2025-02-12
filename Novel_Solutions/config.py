

# used for creating secret keys for flask

import secrets

# Generate a secure random string (hexadecimal)
SECRET_KEY = secrets.token_hex(24)

# print secret key for copying to .env
print (SECRET_KEY)