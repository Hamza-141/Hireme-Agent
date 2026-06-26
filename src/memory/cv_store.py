"""In-memory CV storage."""

_cv_data = None


def save_cv(cv_dict: dict) -> None:
    """Save a CV dict to memory."""
    global _cv_data
    _cv_data = cv_dict


def get_cv() -> dict | None:
    """Retrieve the stored CV dict, or None if nothing is loaded."""
    return _cv_data


def clear_cv() -> None:
    """Clear the stored CV from memory."""
    global _cv_data
    _cv_data = None


def has_cv() -> bool:
    """Return True if a CV is currently loaded, False otherwise."""
    return _cv_data is not None
