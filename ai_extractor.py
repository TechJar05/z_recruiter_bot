from openai import OpenAI
from decouple import config
import json
import re

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def fallback_address_extraction(resume_text: str) -> dict:
    """
    Fallback function to extract address information using pattern matching
    when AI fails to capture address details properly.
    """
    address_info = {"residential_address": "N/A", "pin_code": "N/A", "city": "N/A"}
    
    # Common address patterns
    pincode_pattern = r'\b\d{6}\b'  # 6-digit pincode
    mumbai_pincode_pattern = r'\b4\d{5}\b'  # Mumbai pincodes start with 4
    
    # Indian cities pattern
    indian_cities = [
        "mumbai", "delhi", "bangalore", "chennai", "kolkata", "pune", "hyderabad",
        "ahmedabad", "jaipur", "surat", "lucknow", "kanpur", "nagpur", "indore",
        "kochi", "thiruvananthapuram", "coimbatore", "madurai", "salem", "tiruchirappalli",
        "visakhapatnam", "bhubaneswar", "guwahati", "patna", "raipur", "bhopal"
    ]
    
    # Address keywords
    address_keywords = [
        "address", "resident", "permanent", "current", "home", "residential",
        "street", "road", "lane", "colony", "sector", "area", "block", 
        "apartment", "flat", "nagar", "city", "town", "village"
    ]
    
    lines = resume_text.split('\n')
    potential_address_lines = []
    
    # Look for lines that might contain address information
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
            
        # Check if line contains address keywords
        has_address_keyword = any(keyword in line_lower for keyword in address_keywords)
        has_city = any(city in line_lower for city in indian_cities)
        has_pincode = re.search(pincode_pattern, line)
        
        if has_address_keyword or has_city or has_pincode:
            # Include this line and potentially the next 2-3 lines for context
            context_lines = []
            for j in range(max(0, i-1), min(len(lines), i+3)):
                if lines[j].strip():
                    context_lines.append(lines[j].strip())
            
            potential_address_lines.extend(context_lines)
    
    # Join potential address lines and clean up
    if potential_address_lines:
        full_address = ' '.join(set(potential_address_lines))  # Remove duplicates
        
        # Extract pincode
        pincode_match = re.search(pincode_pattern, full_address)
        if pincode_match:
            address_info["pin_code"] = pincode_match.group()
        
        # Extract city
        for city in indian_cities:
            if city in full_address.lower():
                address_info["city"] = city.title()
                break
        
        # Clean and set address
        # Remove email, phone patterns from address
        cleaned_address = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', full_address)
        cleaned_address = re.sub(r'\b\d{10}\b', '', cleaned_address)  # Remove 10-digit phone numbers
        cleaned_address = re.sub(r'\s+', ' ', cleaned_address).strip()
        
        if len(cleaned_address) > 10:  # Reasonable address length
            address_info["residential_address"] = cleaned_address
    
    return address_info

def extract_resume_data_with_ai(resume_text: str) -> dict:
    prompt = f"""
You are an intelligent resume parser. Your task is to extract structured information from the given resume text.

The resume may use different headings for the same information. Use context to infer meaning even if field names vary.

Common variations include:
- Name → Full Name, Candidate Name
- Phone → Mobile, Contact Number, Phone Number
- DOB → Date of Birth, Birth Date, D.O.B
- Email → Email ID, Email Address
- Address → Residential Address, Permanent Address, Location, Current Address, Home Address
- Experience → Work History, Professional Experience, Employment History
- Education → Academic Background, Qualifications
- Skills → Technical Skills, Functional Skills, Soft Skills, Tools
- Achievements → Accomplishments, Awards, Honors

Use your semantic understanding to detect and extract the correct information from this resume.
Prioritize information that appears in dedicated sections for personal details.

**For address extraction: Extract ANY address information that appears to be the candidate's personal/residential address. This can include:**
- Complete addresses with house numbers, street names, city, state, pincode
- Partial addresses with just city, state, and pincode
- Even just city and state combinations
- Addresses from contact information sections
**Do NOT extract addresses from work experience, company locations, or project details.**

**If you find any residential/personal address information (even partial), extract it. Do not return "N/A" unless there's absolutely no address information.**
**For other fields like 'date_of_birth' or 'hobbies', if not clearly mentioned, return "N/A".**

Resume:
\"\"\"
{resume_text}
\"\"\"

Extract and return only this JSON structure:
{{
  "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "",
  "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",

  "resume_summary": "",
  "industry": "",

  "achievements_and_awards": [{{"year": "", "context": ""}}],

  "work_experience": [
    {{
      "company_name": "", "start_date": "", "end_date": "",
      "industry": "", "designation": "", "department": ""
    }}
  ],

  "education": [
    {{
      "degree": "", "institution_name": "",
      "year_of_passing": "", "grade": ""
    }}
  ],

  "certifications": [
    {{
      "course_name": "", "platform": "", "certification_url": ""
    }}
  ],

  "skills_and_technologies": {{
    "functional_skills": [],
    "technical_skills": [],
    "software_tools": [],
    "soft_skills": []
  }},

  "languages_known": [
    {{
      "language": "",
      "proficiency": ""
    }}
  ],

  "hobbies": [],
  "extra_curricular_activities": [],

  "linkedin_profile": "", "github_link": "", "personal_website": "",
  "expected_salary": "", "current_salary": ""
}}

Guidelines:
- Handle all kinds of resumes (chronological, functional, modern, classic).
- Be flexible with synonyms, formats, and section variations.
- Use semantic understanding to extract fields even if they appear under different names or with line breaks (e.g., "Date of Birth:\\n01/01/1990").
- Do NOT include markdown, explanations, or formatting — just return clean valid JSON.
- For 'residential_address' field, extract ANY personal/residential address information found, even if partial (city, state, pincode combinations are acceptable).
- For any field not found or unclear, return "N/A" or empty array/object as per the JSON structure.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume parser that uses semantic understanding and returns structured JSON. Prioritize accuracy and context. Be liberal in extracting address information - any residential/personal address details should be captured."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )

        raw_content = response.choices[0].message.content.strip()
        print("=== RAW AI RESPONSE ===")
        print(raw_content)

        if not raw_content:
            return {"error": "AI returned empty content."}

        # Remove Markdown formatting if present
        cleaned = re.sub(r"^```json|```$", "", raw_content.strip(), flags=re.MULTILINE)

        try:
            parsed_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            return {
                "error": "JSON decoding error",
                "details": str(e),
                "ai_response": raw_content
            }

        # Improved address validation - be more liberal in accepting addresses
        address = parsed_data.get("residential_address", "").strip()
        if address and address.lower() != "n/a":
            # Accept address if it has any of these patterns:
            # 1. Contains digits (house numbers, pincodes)
            # 2. Contains common address keywords
            # 3. Contains Indian city/state names
            # 4. Has length > 10 (reasonable address length)
            
            indian_locations = [
                "mumbai", "delhi", "bangalore", "chennai", "kolkata", "pune", "hyderabad", 
                "ahmedabad", "jaipur", "surat", "lucknow", "kanpur", "nagpur", "indore",
                "maharashtra", "karnataka", "tamil nadu", "gujarat", "rajasthan", "kerala",
                "punjab", "uttar pradesh", "west bengal", "bihar", "telangana", "andhra pradesh"
            ]
            
            address_lower = address.lower()
            has_digits = re.search(r'\d', address)
            has_keywords = any(kw in address_lower for kw in [
                "street", "road", "lane", "colony", "sector", "area", "block", 
                "apartment", "flat", "nagar", "city", "town", "village", "dist",
                "district", "pincode", "pin", "zip"
            ])
            has_indian_location = any(loc in address_lower for loc in indian_locations)
            sufficient_length = len(address) >= 5
            
            # Keep address if any validation criteria is met
            if not (has_digits or has_keywords or has_indian_location or sufficient_length):
                print(f"Address rejected: '{address}' - No valid criteria met")
                parsed_data["residential_address"] = "N/A"
                parsed_data["pin_code"] = "N/A"
            else:
                print(f"Address accepted: '{address}'")
        else:
            parsed_data["residential_address"] = "N/A"
            parsed_data["pin_code"] = "N/A"

        # Apply fallback address extraction if AI failed to find address
        if (parsed_data.get("residential_address") == "N/A" or 
            not parsed_data.get("residential_address")):
            print("=== APPLYING FALLBACK ADDRESS EXTRACTION ===")
            fallback_data = fallback_address_extraction(resume_text)
            
            if fallback_data["residential_address"] != "N/A":
                print(f"Fallback found address: {fallback_data['residential_address']}")
                parsed_data.update(fallback_data)

        # Standardize string fields to "N/A" if empty
        single_fields = [
            "full_name", "contact_number", "email_address", "date_of_birth", "gender",
            "marital_status", "nationality", "resume_summary", "industry",
            "linkedin_profile", "github_link", "personal_website",
            "expected_salary", "current_salary"
        ]
        for field in single_fields:
            if not parsed_data.get(field) or parsed_data.get(field) == "":
                parsed_data[field] = "N/A"

        # Set empty lists where applicable
        list_fields = [
            "achievements_and_awards", "work_experience", "education", "certifications",
            "languages_known", "hobbies", "extra_curricular_activities"
        ]
        for field in list_fields:
            if not isinstance(parsed_data.get(field), list):
                parsed_data[field] = []
            elif len(parsed_data[field]) == 0:
                parsed_data[field] = []

        # Ensure nested skill categories exist and are lists
        if "skills_and_technologies" not in parsed_data or not isinstance(parsed_data["skills_and_technologies"], dict):
            parsed_data["skills_and_technologies"] = {
                "functional_skills": [],
                "technical_skills": [],
                "software_tools": [],
                "soft_skills": []
            }
        else:
            for skill in ["functional_skills", "technical_skills", "software_tools", "soft_skills"]:
                if not isinstance(parsed_data["skills_and_technologies"].get(skill), list):
                    parsed_data["skills_and_technologies"][skill] = []

        return parsed_data

    except Exception as e:
        print("Unexpected error:", str(e))
        return {"error": str(e)}