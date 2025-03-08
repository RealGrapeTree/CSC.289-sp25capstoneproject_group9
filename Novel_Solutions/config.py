import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(24)
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Debug: Print out values to check if they are loaded
print(f"SECRET_KEY: {Config.SECRET_KEY}")
print(f"STRIPE_SECRET_KEY: {Config.STRIPE_SECRET_KEY}")
print(f"STRIPE_PUBLISHABLE_KEY: {Config.STRIPE_PUBLISHABLE_KEY}")
print(f"STRIPE_WEBHOOK_SECRET: {Config.STRIPE_WEBHOOK_SECRET}")
