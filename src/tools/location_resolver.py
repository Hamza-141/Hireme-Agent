"""
Maps a free-text location string to an Adzuna country code.

Adzuna supports only 12 countries. If the user's location doesn't match
any of them, we return (None, warning_message) so the UI can warn them.
"""

# ── Supported Adzuna countries ────────────────────────────────────────────────

# Maps lowercase keywords → Adzuna country code
_COUNTRY_MAP: dict[str, str] = {
    # United Kingdom
    "uk": "gb", "united kingdom": "gb", "britain": "gb", "great britain": "gb",
    "england": "gb", "scotland": "gb", "wales": "gb", "northern ireland": "gb",
    "london": "gb", "manchester": "gb", "birmingham": "gb", "leeds": "gb",
    "glasgow": "gb", "liverpool": "gb", "edinburgh": "gb", "bristol": "gb",

    # United States
    "us": "us", "usa": "us", "united states": "us", "america": "us",
    "new york": "us", "los angeles": "us", "chicago": "us", "houston": "us",
    "san francisco": "us", "seattle": "us", "boston": "us", "austin": "us",
    "dallas": "us", "miami": "us", "washington": "us", "denver": "us",

    # Australia
    "australia": "au", "au": "au", "sydney": "au", "melbourne": "au",
    "brisbane": "au", "perth": "au", "adelaide": "au", "canberra": "au",

    # Canada
    "canada": "ca", "ca": "ca", "toronto": "ca", "vancouver": "ca",
    "montreal": "ca", "calgary": "ca", "ottawa": "ca", "edmonton": "ca",

    # Germany
    "germany": "de", "de": "de", "deutschland": "de", "berlin": "de",
    "munich": "de", "hamburg": "de", "frankfurt": "de", "cologne": "de",

    # France
    "france": "fr", "fr": "fr", "paris": "fr", "lyon": "fr",
    "marseille": "fr", "toulouse": "fr", "nice": "fr", "bordeaux": "fr",

    # India
    "india": "in", "in": "in", "mumbai": "in", "delhi": "in",
    "bangalore": "in", "bengaluru": "in", "hyderabad": "in", "chennai": "in",
    "pune": "in", "kolkata": "in", "ahmedabad": "in", "noida": "in",
    "gurgaon": "in", "gurugram": "in",

    # New Zealand
    "new zealand": "nz", "nz": "nz", "auckland": "nz", "wellington": "nz",
    "christchurch": "nz",

    # Poland
    "poland": "pl", "pl": "pl", "warsaw": "pl", "krakow": "pl",
    "wroclaw": "pl", "gdansk": "pl", "poznan": "pl",

    # South Africa
    "south africa": "za", "za": "za", "johannesburg": "za", "cape town": "za",
    "durban": "za", "pretoria": "za",

    # Brazil
    "brazil": "br", "br": "br", "são paulo": "br", "sao paulo": "br",
    "rio de janeiro": "br", "brasilia": "br",

    # Austria
    "austria": "at", "at": "at", "vienna": "at", "graz": "at",
    "linz": "at", "salzburg": "at",
}

# Human-readable names for display in warnings
_CODE_TO_NAME: dict[str, str] = {
    "gb": "United Kingdom", "us": "United States", "au": "Australia",
    "ca": "Canada", "de": "Germany", "fr": "France", "in": "India",
    "nz": "New Zealand", "pl": "Poland", "za": "South Africa",
    "br": "Brazil", "at": "Austria",
}

SUPPORTED_COUNTRIES = list(_CODE_TO_NAME.values())


def resolve_location(location: str) -> tuple[str, str | None]:
    """
    Given a free-text location string, return (adzuna_country_code, warning).

    - If the location matches a supported country/city, returns (code, None).
    - If the location is ambiguous or unsupported, returns (fallback_code, warning_message).

    Args:
        location: The raw location string from the user (e.g. "Pakistan", "London", "New York").

    Returns:
        A tuple of (country_code, warning_or_None).
        country_code is always a valid Adzuna code (falls back to "gb" if unknown).
        warning is a string message to show the user, or None if all is fine.
    """
    lowered = location.strip().lower()

    # Direct or partial match
    for keyword, code in _COUNTRY_MAP.items():
        if keyword in lowered:
            return code, None

    # No match — unsupported country/location
    supported_list = ", ".join(sorted(SUPPORTED_COUNTRIES))
    warning = (
        f"⚠️ **'{location}' is not a supported Adzuna region.** "
        f"Adzuna only covers: {supported_list}. "
        f"Showing results for the **United Kingdom** instead. "
        f"Try a city like *London*, *New York*, *Mumbai*, or *Sydney*."
    )
    return "gb", warning
