from openai import OpenAI
from decouple import config
import json
import re

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def extract_resume_data_with_ai(resume_text: str) -> dict:
    prompt = f"""
You are an intelligent resume parser. Your task is to extract structured information from the given resume text.

The resume may use different headings for the same information. Use context to infer meaning even if field names vary.

Common variations include:
- Name → Full Name, Candidate Name
- Phone → Mobile, Contact Number, Phone Number
- DOB → Date of Birth, Birth Date, D.O.B
- Email → Email ID, Email Address
- Address → Residential Address, Permanent Address, Location, Current Address, Home Address, Present Address
- Experience → Work History, Professional Experience, Employment History
- Education → Academic Background, Qualifications
- Skills → Technical Skills, Functional Skills, Soft Skills, Tools
- Achievements → Accomplishments, Awards, Honors

**CRITICAL ADDRESS EXTRACTION GUIDELINES:**
- Extract the candidate's personal residential address ONLY
- Look for addresses in personal details/contact information sections
- Indian addresses often include: Building name, Area/Locality, City, State, PIN
- Accept addresses that include: Apartment numbers, Building names, Colony names, Area names, Sector numbers
- DO NOT extract company addresses from work experience
- DO NOT extract college addresses from education section
- If you find a complete residential address, extract it even without traditional keywords like "street" or "road"
- Extract PIN codes found near addresses (6-digit or 3-digit Mumbai format)

**If a field like 'date_of_birth' or 'hobbies' is not explicitly mentioned or clearly identifiable, return "N/A" for that field.**

Resume:
\"\"\"
{resume_text}
\"\"\"

Extract and return only this JSON structure:
{{
  "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "",
  "gender": "", "marital_status": "", "nationality": "", "address": "", "pin_code": "",

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
- Use semantic understanding to extract fields even if they appear under different names or with line breaks.
- For 'address' field, prioritize personal/residential addresses from contact sections.
- Indian addresses are valid even without "street/road" keywords if they contain building/area/locality information.
- Extract PIN codes that appear near addresses (6-digit or 3-digit Mumbai style).
- Do NOT include markdown, explanations, or formatting — just return clean valid JSON.
- For any field not found or unclear, return "N/A" or empty array/object as per the JSON structure.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume parser specialized in Indian resumes. You understand Indian address formats and extract personal residential addresses accurately. Return only valid JSON."
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

        # More flexible address validation for Indian addresses
        address = parsed_data.get("address", "").strip()
        if address and address.lower() != "n/a":
            # Check if it's a meaningful address (not just a city name)
            if is_valid_indian_address(address):
                parsed_data["address"] = address
            else:
                print(f"Address validation failed for: {address}")
                parsed_data["address"] = "N/A"
                parsed_data["pin_code"] = "N/A"
        else:
            parsed_data["address"] = "N/A"
            parsed_data["pin_code"] = "N/A"

        # Standardize string fields to "N/A" if empty
        single_fields = [
            "full_name", "contact_number", "email_address", "date_of_birth", "gender",
            "marital_status", "nationality", "resume_summary", "industry",
            "linkedin_profile", "github_link", "personal_website",
            "expected_salary", "current_salary"
        ]
        for field in single_fields:
            if not parsed_data.get(field) or str(parsed_data.get(field)).strip() in ["", "null", "None"]:
                parsed_data[field] = "N/A"

        # Set empty lists where applicable
        list_fields = [
            "achievements_and_awards", "work_experience", "education", "certifications",
            "languages_known", "hobbies", "extra_curricular_activities"
        ]
        for field in list_fields:
            if not isinstance(parsed_data.get(field), list):
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

def is_valid_indian_address(address: str) -> bool:
    """
    Validates if the given text is a meaningful Indian address.
    More flexible than the previous validation.
    """
    if not address or len(address.strip()) < 10:
        return False
    
    address_lower = address.lower().strip()
    
    # Reject if it's just a city/state name
    single_word_cities = ["mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad", "pune", "ahmedabad"]
    if address_lower in single_word_cities:
        return False
    
    # Check for address indicators (more flexible than before)
    address_indicators = [
        # Traditional indicators
        "street", "road", "lane", "colony", "sector", "area", "block", "apartment", "flat",
        # Indian specific indicators
        "nagar", "gali", "marg", "chowk", "society", "complex", "residency", "enclave",
        "layout", "extension", "cross", "main", "phase", "wing", "tower", "building",
        "plot", "house", "bungalow", "villa", "row", "quarters", "estate", "park",
        # Abbreviations
        "apt", "bldg", "soc", "co-op", "chs", "hsg", "res"
    ]
    
    # Check if address has indicators OR has structural elements
    has_indicators = any(indicator in address_lower for indicator in address_indicators)
    has_numbers = bool(re.search(r'\d', address))
    has_commas = ',' in address  # Indicates structured address
    has_multiple_words = len(address.split()) >= 3
    
    # Accept if it has indicators OR if it's structured with numbers and multiple components
    if has_indicators:
        return True
    elif has_numbers and has_commas and has_multiple_words:
        return True
    elif has_numbers and has_multiple_words and len(address.split()) >= 4:
        return True
    
    return False

def regenerate_resume_summary(resume_text: str, summary_type: str) -> str:
    """Generate resume or work summary using AI"""
    if summary_type == "resume":
        prompt = f"""
Based on the following resume text, create a professional 2-3 sentence resume summary that highlights the candidate's key strengths, experience, and value proposition:

{resume_text[:1000]}

Return only the summary text, no additional formatting or explanations.
"""
    else:  # work summary
        prompt = f"""
Based on the following resume text, create a professional 2-3 sentence work experience summary that highlights the candidate's key professional achievements and expertise:

{resume_text[:1000]}

Return only the summary text, no additional formatting or explanations.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer. Create concise, impactful summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating {summary_type} summary:", str(e))
        return "N/A"

def extract_address_from_text(text: str) -> str:
    """
    Fallback method to extract address from raw text when AI fails.
    """
    lines = text.split('\n')
    potential_addresses = []
    
    # Look for address patterns in text
    address_keywords = [
        'address', 'residence', 'home', 'permanent', 'current', 'residential',
        'location', 'present address', 'correspondence'
    ]
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
            
        # Look for address section headers
        if any(keyword in line_lower for keyword in address_keywords):
            # Check next few lines for actual address content
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line = lines[j].strip()
                if next_line and is_valid_indian_address(next_line):
                    potential_addresses.append(next_line)
        
        # Look for lines that look like addresses directly
        elif is_valid_indian_address(line):
            # Make sure it's not in work experience or education section
            context_lines = ' '.join(lines[max(0, i-3):i+3]).lower()
            exclude_keywords = ['company', 'organization', 'college', 'university', 'school', 'institute', 'experience', 'worked']
            
            if not any(keyword in context_lines for keyword in exclude_keywords):
                potential_addresses.append(line.strip())
    
    # Return the first valid address found
    return potential_addresses[0] if potential_addresses else "N/A"