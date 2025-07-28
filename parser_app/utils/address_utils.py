import re

def extract_possible_locations(address):
    """
    Extracts possible city or district names from a given address string.
    Cleans out prefixes and symbols like 'Dist.', 'Taluka-', etc.
    """
    address = address.lower()

    # Remove known prefixes
    address = re.sub(r'\b(dist\.?|district|tal\.?|taluka|teh\.?)\-?', '', address)

    # Split by common delimiters
    parts = [part.strip().title() for part in re.split(r'[,\-/|]', address) if part.strip()]

    # Filter out invalid tokens
    seen = set()
    locations = []
    for part in parts:
        if part not in seen and part and part.replace(" ", "").isalpha():
            seen.add(part)
            locations.append(part)

    return locations
