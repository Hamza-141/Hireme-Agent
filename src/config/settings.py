"""Application settings loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "gb")

_required_keys = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "ADZUNA_APP_ID": ADZUNA_APP_ID,
    "ADZUNA_APP_KEY": ADZUNA_APP_KEY,
}

_missing = [name for name, value in _required_keys.items() if not value]

if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Please set them in your .env file."
    )
