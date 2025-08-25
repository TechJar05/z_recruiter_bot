

# import re

# def normalize_linkedin_url(value: str) -> str:
#     """
#     Normalize LinkedIn URL to a clean, full URL.
#     Handles messy inputs from resumes.
#     """
#     if not value:
#         return ""

#     value = value.strip()

#     # Remove any existing protocol (http, https)
#     value = re.sub(r'^https?://', '', value, flags=re.IGNORECASE)

#     # Remove www. if present
#     value = re.sub(r'^www\.', '', value, flags=re.IGNORECASE)

#     # Remove query parameters or fragments
#     value = re.sub(r'[\?#].*$', '', value)

#     # Remove duplicate linkedin.com
#     value = re.sub(r'linkedin\.com/(https?:/)+', 'linkedin.com/', value, flags=re.IGNORECASE)

#     # If value starts with just 'in/', 'pub/', or 'company/', prepend linkedin.com/
#     if re.match(r'^(in/|pub/|company/)', value, flags=re.IGNORECASE):
#         value = 'linkedin.com/' + value.lstrip('/')

#     # If it doesn’t contain linkedin.com yet, assume it's a short username and prepend
#     if 'linkedin.com' not in value.lower():
#         value = 'linkedin.com/in/' + value.lstrip('/')

#     # Prepend https://
#     value = 'https://' + value

#     # Remove trailing slashes
#     value = value.rstrip('/')

#     return value




import re

def normalize_linkedin_url(value: str) -> str:
    """
    Normalize LinkedIn URL to a clean, full URL.
    Handles messy inputs from resumes.
    """
    if not value:
        return ""

    value = value.strip()

    # 🔥 Remove leading @ (usernames often start with this in resumes)
    value = re.sub(r'^@', '', value)

    # Remove any existing protocol (http, https)
    value = re.sub(r'^https?://', '', value, flags=re.IGNORECASE)

    # Remove www. if present
    value = re.sub(r'^www\.', '', value, flags=re.IGNORECASE)

    # Remove query parameters or fragments
    value = re.sub(r'[\?#].*$', '', value)

    # Remove duplicate linkedin.com
    value = re.sub(r'linkedin\.com/(https?:/)+', 'linkedin.com/', value, flags=re.IGNORECASE)

    # If value starts with just 'in/', 'pub/', or 'company/', prepend linkedin.com/
    if re.match(r'^(in/|pub/|company/)', value, flags=re.IGNORECASE):
        value = 'linkedin.com/' + value.lstrip('/')

    # If it doesn’t contain linkedin.com yet, assume it's a short username and prepend
    if 'linkedin.com' not in value.lower():
        value = 'linkedin.com/in/' + value.lstrip('/')

    # Prepend https://
    value = 'https://' + value

    # Remove trailing slashes
    value = value.rstrip('/')

    return value
