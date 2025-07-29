import re
from datetime import datetime
from dateutil import parser
from parser_app.utils.address_helpers import get_pincode_by_city
from parser_app.utils.address_utils import extract_possible_locations

INDIAN_STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Rajasthan", "Kerala", "Punjab", "Delhi",
    "Uttar Pradesh", "West Bengal", "Bihar", "Telangana", "Andhra Pradesh", "Madhya Pradesh", "Odisha"
]

def detect_nationality(phone_number: str) -> str:
    digits = ''.join(filter(str.isdigit, phone_number))
    if digits.startswith('91') and len(digits) == 12:
        return "Indian"
    elif len(digits) == 10 and digits[0] in "6789":
        return "Indian"
    return "Unknown"

def correct_mumbai_pincode(pincode: str) -> str:
    pincode = pincode.strip()
    if len(pincode) == 3:
        return "400" + pincode
    elif len(pincode) == 6:
        return pincode
    return ""

def clean_indian_phone_number(number):
    if not number:
        return ""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", number)
    # Remove country code if present (assume Indian number)
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[-10:]
    return digits

def extract_pincode_from_text(text: str) -> str:
    """
    Extracts Indian pincode from messy address text.
    Supports:
    - Full 6-digit pincodes (e.g., 110001, 400076)
    - Mumbai-style 3-digit suffixes (e.g., "-055" → 400055)
    """
    text = text.strip()

    # Priority: Match full Indian pincode (6 digits)
    match6 = re.search(r'\b\d{6}\b', text)
    if match6:
        return match6.group()

    # Match Mumbai-style suffixes: e.g., "-055", " 055", "Mumbai-055"
    match3 = re.search(r'\b-?(\d{3})\b', text)
    if match3:
        return "400" + match3.group(1)

    return ""

def enrich_address_with_pincode(parsed_resume: dict) -> dict:
    raw_pin = parsed_resume.get("pin_code", "").strip()
    address = parsed_resume.get("address", "").strip()
    print(f"Enriching address with pincode: {address}, raw pin: {raw_pin}")

    corrected_pin = ""

    # STEP 1: Correct existing pin
    if raw_pin and raw_pin != "N/A":
        if len(raw_pin) == 3:
            corrected_pin = "400" + raw_pin
        elif len(raw_pin) == 6 and raw_pin.isdigit():
            corrected_pin = raw_pin

    # STEP 2: Extract from address if missing
    if not corrected_pin and address != "N/A":
        corrected_pin = extract_pincode_from_text(address)

    # STEP 3: Try extracting city/district from address
    if not corrected_pin and address != "N/A":
        possible_locations = extract_possible_locations(address)
        print(f"Trying locations for pin lookup: {possible_locations}")

        for location in possible_locations:
            fetched_pin = get_pincode_by_city(location)
            if fetched_pin:
                corrected_pin = fetched_pin
                print(f"Pincode found using location '{location}': {corrected_pin}")
                break

    # STEP 4: Extract city for separate field
    city = extract_city_from_address(address)
    if city:
        parsed_resume["city"] = city

    # STEP 5: Clean address and assign values
    if corrected_pin:
        cleaned_address = re.sub(r'\b-?\d{3,6}\b', '', address).strip(', ')
        parsed_resume["pin_code"] = corrected_pin
        parsed_resume["address"] = cleaned_address
    else:
        parsed_resume["pin_code"] = "N/A"

    return parsed_resume

def extract_city_from_address(address: str) -> str:
    """Extract city name from address"""
    if not address or address == "N/A":
        return "N/A"
    
    # Common Indian cities
    indian_cities = [
        "Mumbai", "Delhi", "Bangalore", "Bengaluru", "Chennai", "Kolkata", "Pune", "Hyderabad",
        "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
        "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad",
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivali",
        "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai",
        "Allahabad", "Prayagraj", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior",
        "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh"
    ]
    
    address_lower = address.lower()
    for city in indian_cities:
        if city.lower() in address_lower:
            return city
    
    # Try to extract from comma-separated address parts
    parts = [part.strip() for part in address.split(',')]
    for part in parts:
        # Check if part looks like a city (capitalized, 3+ chars, no numbers)
        if (len(part) >= 3 and 
            part[0].isupper() and 
            not re.search(r'\d', part) and
            part not in ['Road', 'Street', 'Lane', 'Colony', 'Sector', 'Area', 'Block']):
            return part
    
    return "N/A"

def fallback_address_extraction(raw_text: str) -> dict:
    """
    Advanced fallback address extraction from raw resume text.
    Uses multiple strategies to find address information.
    """
    result = {"address": "N/A", "pin_code": "N/A", "city": "N/A"}
    
    # Import the AI fallback function
    from .ai_extractor import extract_address_from_text
    
    # Try AI-based fallback extraction
    extracted_address = extract_address_from_text(raw_text)
    if extracted_address != "N/A":
        result["address"] = extracted_address
        
        # Try to extract pincode and city from found address
        pincode = extract_pincode_from_text(extracted_address)
        if pincode:
            result["pin_code"] = pincode
            
        city = extract_city_from_address(extracted_address)
        if city != "N/A":
            result["city"] = city
    
    # Additional pattern-based extraction if AI failed
    if result["address"] == "N/A":
        result.update(pattern_based_address_extraction(raw_text))
    
    return result

def pattern_based_address_extraction(text: str) -> dict:
    """
    Pattern-based address extraction as final fallback
    """
    result = {"address": "N/A", "pin_code": "N/A", "city": "N/A"}
    
    lines = text.split('\n')
    
    # Look for address-like patterns
    address_patterns = [
        r'(?i)address[:\s]*(.{10,100})',
        r'(?i)residence[:\s]*(.{10,100})',
        r'(?i)home[:\s]*(.{10,100})',
        r'(?i)permanent[:\s]*(.{10,100})',
        r'(?i)current[:\s]*(.{10,100})'
    ]
    
    for line in lines:
        for pattern in address_patterns:
            match = re.search(pattern, line)
            if match:
                potential_address = match.group(1).strip()
                if len(potential_address) > 15:  # Reasonable address length
                    result["address"] = potential_address
                    
                    # Extract pincode
                    pincode = extract_pincode_from_text(potential_address)
                    if pincode:
                        result["pin_code"] = pincode
                    
                    # Extract city
                    city = extract_city_from_address(potential_address)
                    if city != "N/A":
                        result["city"] = city
                    
                    return result
    
    return result

def enrich_resume_data(data: dict, raw_text: str) -> dict:
    phone = data.get("contact_number", "").replace(" ", "")
    address = data.get("address", "").lower()
    state_mentioned = any(state.lower() in address for state in INDIAN_STATES)

    # Apply fallback address extraction if address is missing
    if not data.get("address") or data.get("address") == "N/A":
        print("=== APPLYING FALLBACK ADDRESS EXTRACTION ===")
        fallback_data = fallback_address_extraction(raw_text)
        
        if fallback_data["address"] != "N/A":
            print(f"Fallback found address: {fallback_data['address']}")
            data.update(fallback_data)

    if detect_nationality(phone) == "Indian" or state_mentioned:
        data["nationality"] = "Indian"
    else:
        data["nationality"] = "Unknown"

    work_ex = data.get("work_experience", [])
    durations, date_ranges = [], []
    currently_employed = False

    for job in work_ex:
        start = job.get("start_date")
        end = job.get("end_date") or datetime.now().strftime("%Y")
        if end.lower() in ['present', 'current', 'till date']:
            currently_employed = True
            end = datetime.now().strftime("%Y-%m")

        try:
            sdate = parser.parse(start)
            edate = parser.parse(end)
            if edate < sdate:
                sdate, edate = edate, sdate
            durations.append((edate - sdate).days / 365.25)
            date_ranges.append((sdate, edate))
        except:
            continue

    def format_duration(duration_years):
        total_months = int(round(duration_years * 12))
        years = total_months // 12
        months = total_months % 12
        parts = []
        if years > 0:
            parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months > 0:
            parts.append(f"{months} month{'s' if months > 1 else ''}")
        return " ".join(parts) if parts else "0 months"

    if durations:
        max_dur = max(durations)
        min_dur = min(durations)
        data["longest_job_duration"] = format_duration(max_dur)
        data["shortest_job_duration"] = format_duration(min_dur)

    career_gaps = []
    if date_ranges:
        date_ranges.sort()
        for i in range(1, len(date_ranges)):
            prev_end = date_ranges[i-1][1]
            curr_start = date_ranges[i][0]
            gap_months = (curr_start - prev_end).days // 30
            if gap_months > 1:
                if gap_months >= 12:
                    years = gap_months // 12
                    months = gap_months % 12
                    gap_text = f"{years} years{' ' + str(months) + ' months' if months else ''} gap between {prev_end.date()} and {curr_start.date()}"
                else:
                    gap_text = f"{gap_months} months gap between {prev_end.date()} and {curr_start.date()}"
                career_gaps.append(gap_text)

    data["career_gaps"] = career_gaps
    data["is_currently_employed"] = currently_employed
    data["contact_number"] = clean_indian_phone_number(data.get("contact_number", ""))
    data = enrich_address_with_pincode(data)
    
    return data