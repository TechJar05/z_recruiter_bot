

# # services/ai_extractor.py

# from openai import OpenAI
# from decouple import config
# import json
# import json
# import re
# client = OpenAI(api_key=config("OPENAI_API_KEY"))



# INDUSTRY_LIST = """
# Fresher, Banking, Insurance, CA Firm, Loan Syndication, Broking & Research, 
# Investment/Wealth Advisory, Rating & Assessment, Other Financial Services, 
# IT - Software, IT - Hardware, IT - Other Services, Real Estate & Infra, 
# Healthcare - Services, Pharmaceutical, Healthcare - Equipment, FMCG/Food/Beverages, 
# Tourism & Hospitality, Retail, Textiles/Garments, BPO/KPO/Call Centres, 
# Engineering/Capital Goods, Telecom Equipment, Telecom Services, 
# Automobile/Auto Components, Consumer Durables/Electronics, Aviation, 
# Agriculture and Allied Industries, Advertisement/Media/Events & Entertainment, 
# Art/Animation/Creative/Crafts, Intermediary Services, Business Consulting, Legal, 
# Support Services, Transport & Related Services, Apparels & Accessories, 
# Architecture/Interior Design, Gems & Jewellery, Cement/Building Material, 
# Chemical/Plastic/Rubber/Glass/Paint, Furnishings/Sanitary ware/Electricals, 
# Military/Police/Arms & Ammunition, Industrial Products, Mining/Metal, Power/Energy, 
# Oil & Gas, Industrial Design, Internet /E-Commerce/Digital Marketing, NGO, 
# Printing/Photography/Paper/Wood, Recruitment Services, Science & Technology, 
# Facility Management, Gift/Stationery, Packaging/Courier, Education & Training, 
# Publishing, Sports/Fitness, Others - Manufacturing, Others - Trading, 
# Others - Services, Handicraft Export, Media & Entertainment, Petrochemical, 
# Environmental Consulting, Logistics, MEP, NBFC, FINTECH
# """



# EDUCATION_LIST = """
# Any Diploma, Hotel Management, Animation, Fashion designing, Architecture, 
# Export-Import, Digital Marketing, 3D for VFX, Web & Graphics, Other Diploma, 
# Financial Risk Manager, Certified Internal Auditor, Chartered Wealth Manager, 
# Certified Financial Planner, Other Certification, 10 +2 or Below, 
# Above 10 +2 but not Graduate, Any Graduate, Bachelor of Accounting and Finance, 
# Bachelor of Archaeology, Bachelor of Arts, Bachelor of Banking & Insurance, 
# Bachelor of Business Administration, Bachelor of Commerce, 
# Bachelor of Computer Applications, Bachelor of Designs, Bachelor of Education, 
# Bachelor of Engineering, Bachelor of Laws, Bachelor of Management Studies, 
# Bachelor of Mass Communications, Bachelor of Pharma, Bachelor of Philosophy, 
# Bachelor of Science, MBBS, BDS, Other - Graduation, Any Post Graduate, CA, 
# CA (Semi Qualified), CFA, CS, ICWA/CMA, Master of Accounting and Finance, 
# Master of Archaeology, Master of Arts, Master of Banking & Insurance, MBA, 
# Master of Commerce, Master of Computer Applications, Master of Designs, 
# Master of Education, Master of Engineering/Technology, Master of Laws, 
# Master of Management Studies, Master of Mass Communications, Master of Pharma, 
# Master of Philosophy, Master of Science, MD/MS, MDS, PHd/Doctorate, 
# Other - Profession/Post Graduation, Bachelor of Science - Information Technology, 
# CA (Intern), Bachelor of Technology, Master of Technology, 
# Architecture (B.Arch/M.Arch)
# """




# def extract_resume_data_with_ai(resume_text: str) -> dict:
#     prompt = f"""
# Given this resume text:

# {resume_text}

# Extract the following structured data in valid JSON format. If any field is missing, infer it from context. If the data is not present or cannot be inferred, leave the value empty.


# Rules for `industry`:
# - Match strictly with one from this list:
# {INDUSTRY_LIST}
# - If no exact match is found, infer from context and append " (AI Inferred)".

# Rules for `education`:
# - Extract all education entries mentioned in the resume (not just one).
# - For each entry, match the degree strictly with one from this list:
# {EDUCATION_LIST}
# - Always normalize abbreviations into their full form (e.g., "B.Com" → "Bachelor of Commerce", "MCA" → "Master of Computer Applications").
# - If the degree or qualification does not match the list exactly or closely, then infer the most appropriate one and append " (AI Inferred)".
# - Preserve other fields like institution_name, year_of_passing, and grade if available.




# {{
#   "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "", 
#   "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",
  
#   "resume_summary": "", 
#   "industry": "",  
#   "overall_work_summary": "",

#   "achievements_and_awards": [{{"year": "", "context": ""}}],

#   "work_experience": [
#     {{
#       "company_name": "", "start_date": "", "end_date": "", 
#       "industry": "", "designation": "", "department": "",
#       "work_summary": ""
#     }}
#   ],

#   "education": [
#     {{
#       "degree": "", "institution_name": "", 
#       "year_of_passing": "", "grade": ""
#     }}
#   ],

#   "certifications": [
#     {{
#       "course_name": "", "platform": "", "certification_url": ""
#     }}
#   ],

#   "skills_and_technologies": {{
#     "functional_skills": [],
#     "technical_skills": [],
#     "software_tools": [],
#     "soft_skills": []
#   }},

#   "languages_known": [
#     {{
#       "language": "", 
#       "proficiency": ""
#     }}
#   ],

#   "hobbies": [],
#   "extra_curricular_activities": [],

#   "linkedin_profile": "", "github_link": "", "personal_website": "", 
#   "expected_salary": "", "current_salary": ""
# }}

# Guidelines:
# - "industry" should reflect the primary domain: Information Technology, Finance, Healthcare, etc.
# - "technical_skills" must include programming languages, libraries, frameworks, APIs.
# - "software_tools" must include only actual software (e.g., VS Code, Git, JIRA, Postman).
# - "functional_skills" are domain-level tasks (e.g., project management, analysis).
# - "soft_skills" should be inferred (e.g., leadership, teamwork) if not directly mentioned.
# - "overall_work_summary" should summarize the candidate’s career across all jobs in 4–6 sentences.
# - Use Basic / Intermediate / Fluent / Native for language proficiency.
# - Make sure the output is valid JSON without markdown, comments, or formatting.
# - Always expand degree abbreviations into their full forms (e.g., "B.Com" → "Bachelor of Commerce", "BE" → "Bachelor of Engineering", "BCA" → "Bachelor of Computer Applications", "MBA" → "Master of Business Administration", etc.).
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a professional resume parser that returns structured JSON and intelligently infers missing details."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#             temperature=0.0,
#             max_tokens=1500
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception as e:
#         return {"error": str(e)}




# services/ai_extractor.py

from openai import OpenAI
from decouple import config
import json
import re
client = OpenAI(api_key=config("OPENAI_API_KEY"))

INDUSTRY_LIST = """
Fresher, Banking, Insurance, CA Firm, Loan Syndication, Broking & Research, 
Investment/Wealth Advisory, Rating & Assessment, Other Financial Services, 
IT - Software, IT - Hardware, IT - Other Services, Real Estate & Infra, 
Healthcare - Services, Pharmaceutical, Healthcare - Equipment, FMCG/Food/Beverages, 
Tourism & Hospitality, Retail, Textiles/Garments, BPO/KPO/Call Centres, 
Engineering/Capital Goods, Telecom Equipment, Telecom Services, 
Automobile/Auto Components, Consumer Durables/Electronics, Aviation, 
Agriculture and Allied Industries, Advertisement/Media/Events & Entertainment, 
Art/Animation/Creative/Crafts, Intermediary Services, Business Consulting, Legal, 
Support Services, Transport & Related Services, Apparels & Accessories, 
Architecture/Interior Design, Gems & Jewellery, Cement/Building Material, 
Chemical/Plastic/Rubber/Glass/Paint, Furnishings/Sanitary ware/Electricals, 
Military/Police/Arms & Ammunition, Industrial Products, Mining/Metal, Power/Energy, 
Oil & Gas, Industrial Design, Internet /E-Commerce/Digital Marketing, NGO, 
Printing/Photography/Paper/Wood, Recruitment Services, Science & Technology, 
Facility Management, Gift/Stationery, Packaging/Courier, Education & Training, 
Publishing, Sports/Fitness, Others - Manufacturing, Others - Trading, 
Others - Services, Handicraft Export, Media & Entertainment, Petrochemical, 
Environmental Consulting, Logistics, MEP, NBFC, FINTECH
"""

EDUCATION_LIST = """
Any Diploma, Hotel Management, Animation, Fashion designing, Architecture, 
Export-Import, Digital Marketing, 3D for VFX, Web & Graphics, Other Diploma, 
Financial Risk Manager, Certified Internal Auditor, Chartered Wealth Manager, 
Certified Financial Planner, Other Certification, 10 +2 or Below, 
Above 10 +2 but not Graduate, Any Graduate, Bachelor of Accounting and Finance, 
Bachelor of Archaeology, Bachelor of Arts, Bachelor of Banking & Insurance, 
Bachelor of Business Administration, Bachelor of Commerce, 
Bachelor of Computer Applications, Bachelor of Designs, Bachelor of Education, 
Bachelor of Engineering, Bachelor of Laws, Bachelor of Management Studies, 
Bachelor of Mass Communications, Bachelor of Pharma, Bachelor of Philosophy, 
Bachelor of Science, MBBS, BDS, Other - Graduation, Any Post Graduate, CA, 
CA (Semi Qualified), CFA, CS, ICWA/CMA, Master of Accounting and Finance, 
Master of Archaeology, Master of Arts, Master of Banking & Insurance, MBA, 
Master of Commerce, Master of Computer Applications, Master of Designs, 
Master of Education, Master of Engineering/Technology, Master of Laws, 
Master of Management Studies, Master of Mass Communications, Master of Pharma, 
Master of Philosophy, Master of Science, MD/MS, MDS, PHd/Doctorate, 
Other - Profession/Post Graduation, Bachelor of Science - Information Technology, 
CA (Intern), Bachelor of Technology, Master of Technology, 
Architecture (B.Arch/M.Arch)
"""

# Create a set of valid degrees for faster lookup
VALID_DEGREES = {
    degree.strip() for degree in EDUCATION_LIST.replace('\n', ', ').split(', ') 
    if degree.strip()
}

def validate_education_degrees(extracted_data: dict) -> dict:
    """
    Validates that all education degrees are from the predefined list.
    If not, maps them to appropriate fallback categories or raises error.
    """
    if 'education' not in extracted_data:
        return extracted_data
    
    # Degree mapping for common abbreviations
    degree_mapping = {
        'BCA': 'Bachelor of Computer Applications',
        'B.C.A': 'Bachelor of Computer Applications',
        'B.Com': 'Bachelor of Commerce',
        'BCom': 'Bachelor of Commerce',
        'B.Tech': 'Bachelor of Technology',
        'BTech': 'Bachelor of Technology',
        'B.E': 'Bachelor of Engineering',
        'BE': 'Bachelor of Engineering',
        'B.Sc': 'Bachelor of Science',
        'BSc': 'Bachelor of Science',
        'B.A': 'Bachelor of Arts',
        'BA': 'Bachelor of Arts',
        'BBA': 'Bachelor of Business Administration',
        'MCA': 'Master of Computer Applications',
        'M.Com': 'Master of Commerce',
        'MCom': 'Master of Commerce',
        'M.Tech': 'Master of Technology',
        'MTech': 'Master of Technology',
        'M.E': 'Master of Engineering/Technology',
        'ME': 'Master of Engineering/Technology',
        'M.Sc': 'Master of Science',
        'MSc': 'Master of Science',
        'M.A': 'Master of Arts',
        'MA': 'Master of Arts',
        '10th': '10 +2 or Below',
        'SSC': '10 +2 or Below',
        'Secondary': '10 +2 or Below',
        'Matriculation': '10 +2 or Below',
        '12th': '10 +2 or Below',
        'HSC': '10 +2 or Below',
        'Higher Secondary': '10 +2 or Below',
        'Intermediate': '10 +2 or Below',
        '+2': '10 +2 or Below',
        'Plus Two': '10 +2 or Below',
    }
    
    validated_education = []
    errors = []
    
    for idx, edu in enumerate(extracted_data['education']):
        degree = edu.get('degree', '').strip()
        
        if not degree:
            # Empty degree, keep as is
            validated_education.append(edu)
            continue
            
        # Check if degree is already in valid list
        if degree in VALID_DEGREES:
            validated_education.append(edu)
            continue
            
        # Try to map using the mapping dictionary
        if degree in degree_mapping:
            edu['degree'] = degree_mapping[degree]
            validated_education.append(edu)
            continue
            
        # Try to find fallback category
        degree_lower = degree.lower()
        
        # School level education
        if any(keyword in degree_lower for keyword in ['10th', '12th', 'ssc', 'hsc', 'secondary', 'matriculation']):
            edu['degree'] = '10 +2 or Below'
            validated_education.append(edu)
            continue
            
        # Diploma
        if 'diploma' in degree_lower:
            edu['degree'] = 'Any Diploma'
            validated_education.append(edu)
            continue
            
        # Bachelor's degrees
        if any(keyword in degree_lower for keyword in ['bachelor', 'b.', 'graduate']):
            edu['degree'] = 'Any Graduate'
            validated_education.append(edu)
            continue
            
        # Master's/Postgraduate degrees
        if any(keyword in degree_lower for keyword in ['master', 'm.', 'post graduate', 'postgraduate']):
            edu['degree'] = 'Any Post Graduate'
            validated_education.append(edu)
            continue
            
        # If we reach here, degree couldn't be mapped
        errors.append(f"Education entry {idx + 1}: Degree '{degree}' not found in predefined list and couldn't be mapped to fallback category")
        # You can choose to either:
        # Option 1: Skip this education entry
        # Option 2: Set degree to empty string
        # Option 3: Throw an error
        
        # Option 2: Set to empty and continue
        edu['degree'] = ''
        validated_education.append(edu)
    
    extracted_data['education'] = validated_education
    
    # Add validation errors to the response
    if errors:
        extracted_data['validation_errors'] = errors
    
    return extracted_data

def extract_resume_data_with_ai(resume_text: str) -> dict:
    prompt = f"""
Given this resume text:

{resume_text}

Extract the following structured data in valid JSON format. If any field is missing, infer it from context. If the data is not present or cannot be inferred, leave the value empty.

Rules for `industry`:
- Match strictly with one from this list:
{INDUSTRY_LIST}
- If no exact match is found, infer from context and append " (AI Inferred)".

Rules for `education` (VERY IMPORTANT - FOLLOW STRICTLY):
- Extract all education entries mentioned in the resume.
- For each education entry, the "degree" field MUST match exactly with one from this predefined list:
{EDUCATION_LIST}

**Degree Mapping Rules:**
- BCA, B.C.A → "Bachelor of Computer Applications"
- B.Com, BCom → "Bachelor of Commerce" 
- B.Tech, BTech → "Bachelor of Technology"
- B.E, BE → "Bachelor of Engineering"
- B.Sc, BSc → "Bachelor of Science"
- B.A, BA → "Bachelor of Arts"
- BBA → "Bachelor of Business Administration"
- MBA → "Master of Business Administration" (Note: Use "MBA" as it exists in the list)
- MCA → "Master of Computer Applications"
- M.Com, MCom → "Master of Commerce"
- M.Tech, MTech → "Master of Technology"
- M.E, ME → "Master of Engineering/Technology"
- M.Sc, MSc → "Master of Science"
- M.A, MA → "Master of Arts"
- 10th, SSC, Secondary, Matriculation → "10 +2 or Below"
- 12th, HSC, Higher Secondary, Intermediate, Plus Two, +2 → "10 +2 or Below"
- Diploma (any type) → "Any Diploma"
- Any graduation degree not specified above → "Any Graduate"
- Any post-graduation degree not specified above → "Any Post Graduate"

**CRITICAL RULES:**
1. The "degree" field must contain ONLY the exact text from the EDUCATION_LIST above. 
2. If you cannot find a close match for any degree mentioned in the resume, use these fallback options:
   - For school level (10th, 12th): "10 +2 or Below"
   - For any bachelor's degree: "Any Graduate" 
   - For any master's/postgraduate degree: "Any Post Graduate"
   - For any diploma: "Any Diploma"
3. DO NOT create new degree names or use degrees not in the list.
4. If a degree cannot be categorized at all, leave the "degree" field empty ("").

Example correct mappings:
- Resume mentions "BCA" → degree: "Bachelor of Computer Applications"
- Resume mentions "10th passed" → degree: "10 +2 or Below"  
- Resume mentions "HSC" → degree: "10 +2 or Below"
- Resume mentions "MBA" → degree: "MBA"

{{
  "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "", 
  "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",
  
  "resume_summary": "", 
  "industry": "",  
  "overall_work_summary": "",

  "achievements_and_awards": [{{"year": "", "context": ""}}],

  "work_experience": [
    {{
      "company_name": "", "start_date": "", "end_date": "", 
      "industry": "", "designation": "", "department": "",
      "work_summary": ""
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
- "industry" should reflect the primary domain: Information Technology, Finance, Healthcare, etc.
- "technical_skills" must include programming languages, libraries, frameworks, APIs.
- "software_tools" must include only actual software (e.g., VS Code, Git, JIRA, Postman).
- "functional_skills" are domain-level tasks (e.g., project management, analysis).
- "soft_skills" should be inferred (e.g., leadership, teamwork) if not directly mentioned.
- "overall_work_summary" should summarize the candidate's career across all jobs in 4–6 sentences.
- Use Basic / Intermediate / Fluent / Native for language proficiency.
- Make sure the output is valid JSON without markdown, comments, or formatting.
- REMEMBER: All degree names must match exactly with the EDUCATION_LIST provided.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume parser that returns structured JSON. You must strictly follow the degree mapping rules and match education degrees exactly with the provided list."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=1500
        )
        
        # Parse the AI response
        ai_result = json.loads(response.choices[0].message.content)
        
        # Validate and fix education degrees
        validated_result = validate_education_degrees(ai_result)
        
        return validated_result
        
    except Exception as e:
        return {"error": str(e)}






def regenerate_resume_summary(text: str, summary_type: str = "resume") -> str:
    """
    Keeps the original name used in your import.
    summary_type: 'resume' | 'work'
    """
    try:
        instruction = (
            "Regenerate a crisp, professional resume summary (3–4 sentences). "
            "Focus on strengths, domain, years of experience (if present), key tools, and impact."
            if summary_type == "resume"
            else
            "Regenerate a concise (2–4 sentences) work summary for this specific role. "
            "Focus on responsibilities, technologies, measurable outcomes, and scope."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert career and resume writer. Return plain text only."},
                {"role": "user", "content": f"{instruction}\n\n--- Input Text ---\n{text}\n"}
            ],
            temperature=0.4,
            max_tokens=220
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
