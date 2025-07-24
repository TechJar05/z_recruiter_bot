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

import re

def enrich_address_with_pincode(parsed_resume: dict) -> dict:
    raw_pin = parsed_resume.get("pin_code", "").strip()
    address = parsed_resume.get("residential_address", "").strip()
    print(f"Enriching address with pincode: {address}, raw pin: {raw_pin}")

    corrected_pin = ""

    # STEP 1: Correct existing pin
    if raw_pin:
        if len(raw_pin) == 3:
            corrected_pin = "400" + raw_pin
        elif len(raw_pin) == 6 and raw_pin.isdigit():
            corrected_pin = raw_pin

    # STEP 2: Extract from address if missing
    if not corrected_pin:
        corrected_pin = extract_pincode_from_text(address)

    # STEP 3: Try extracting city/district from address
    if not corrected_pin:
        possible_locations = extract_possible_locations(address)
        print(f"Trying locations for pin lookup: {possible_locations}")

        for location in possible_locations:
            fetched_pin = get_pincode_by_city(location)
            if fetched_pin:
                corrected_pin = fetched_pin
                print(f"Pincode found using location '{location}': {corrected_pin}")
                break

    # STEP 4: Clean address and assign values
    if corrected_pin:
        cleaned_address = re.sub(r'\b-?\d{3,6}\b', '', address).strip(', ')
        parsed_resume["pin_code"] = corrected_pin
        parsed_resume["residential_address"] = cleaned_address
    else:
        parsed_resume["pin_code"] = "N/A"

    return parsed_resume


def enrich_resume_data(data: dict, raw_text: str) -> dict:
    phone = data.get("contact_number", "").replace(" ", "")
    address = data.get("residential_address", "").lower()
    state_mentioned = any(state.lower() in address for state in INDIAN_STATES)

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

    if durations:
        data["longest_job_duration"] = f"{int(max(durations))} years" if max(durations) >= 1 else f"{int(max(durations)*12)} months"
        data["shortest_job_duration"] = f"{int(min(durations))} years" if min(durations) >= 1 else f"{int(min(durations)*12)} months"

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
    data = enrich_address_with_pincode(data)
    return data
