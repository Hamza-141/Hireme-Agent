"""Application settings loaded from environment variables or Streamlit secrets."""

import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = None) -> str:
    """Read a config value from Streamlit secrets (cloud) or .env (local)."""
    # Try Streamlit secrets first (only available when running on Streamlit Cloud)
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    # Fall back to environment variable / .env file
    return os.getenv(key, default)


GROQ_API_KEY = _get("GROQ_API_KEY")
ADZUNA_APP_ID = _get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = _get("ADZUNA_APP_KEY")
ADZUNA_COUNTRY = _get("ADZUNA_COUNTRY", "gb")

_required_keys = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "ADZUNA_APP_ID": ADZUNA_APP_ID,
    "ADZUNA_APP_KEY": ADZUNA_APP_KEY,
}

_missing = [name for name, value in _required_keys.items() if not value]

if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Please set them in your .env file or Streamlit secrets."
    )
