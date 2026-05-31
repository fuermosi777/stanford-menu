import os

# Pure Python .env file parser (replaces python-dotenv to keep dependencies minimal and avoid sandbox issues)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    os.environ[key] = val
    except Exception as e:
        # Silently ignore or print error if needed, fallback to environment
        pass

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# SMTP settings (defaults to Gmail)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Dining Preferences
DINING_HALL = os.getenv("DINING_HALL", "Arrillaga")
MEAL_TYPE = os.getenv("MEAL_TYPE", "Lunch")
