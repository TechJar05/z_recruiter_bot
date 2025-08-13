import re

def normalize_linkedin_url(value: str) -> str:
    """
    Clean and normalize LinkedIn URL.

    Examples:
        'linkedin.com/in/john-doe' -> 'https://www.linkedin.com/in/john-doe'
        'www.linkedin.com/in/john-doe/' -> 'https://www.linkedin.com/in/john-doe'
        '' -> ''
    """
    if not value:
        return ""

    value = value.strip()

    # Add https if missing
    if not value.startswith("http"):
        value = "https://" + value

    # Ensure it contains linkedin.com
    if "linkedin.com" not in value.lower():
        return ""

    # Remove trailing slashes
    value = value.rstrip("/")

    # Optional: remove query parameters
    value = re.sub(r"\?.*$", "", value)

    return value
