from openai import OpenAI
from decouple import config
import json

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def extract_resume_data_with_ai(resume_text: str) -> dict:
#     prompt = f"""
# Given this resume text:

# {resume_text}

# Extract this data in JSON format. If any field is missing in the resume, infer it based on content or leave it empty:

# {{
#   "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "", 
#   "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",
  
#   "resume_summary": "", 
#   "industry": "",  

#   "achievements_and_awards": [{{"year": "", "context": ""}}],
  
#   "work_experience": [
#     {{
#       "company_name": "", "start_date": "", "end_date": "", 
#       "industry": "", "designation": "", "department": ""
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
#     "software_tools": []
#   }},

#   "languages_known": [
#     {{
#       "language": "", "proficiency": ""
#     }}
#   ],

#   "hobbies": [],
#   "extra_curricular_activities": [],

#   "linkedin_profile": "", "github_link": "", "personal_website": "", 
#   "expected_salary": "", "current_salary": ""
# }}

# Guidelines:
# - "industry" should reflect the most relevant industry: IT, Finance, Healthcare, etc.
# - Separate technical skills, functional skills, and software tools appropriately.
# - Infer hobbies and extra-curriculars based on context if not explicitly mentioned.
# - For each known language, include proficiency level: Basic, Intermediate, Fluent, or Native.
# """
    prompt = f"""
Given this resume text:

{resume_text}

Extract the following structured data in valid JSON format. If any field is missing, infer it from context. If the data is not present or cannot be inferred, leave the value empty.

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
- "industry" should reflect the primary domain: IT, Finance, Healthcare, etc.
- "technical_skills" must include programming languages, libraries, frameworks, APIs.
- "software_tools" must include only actual software (e.g., VS Code, Git, JIRA, Postman).
- "functional_skills" are domain-level tasks (e.g., project management, analysis).
- "soft_skills" should be inferred (e.g., leadership, teamwork) if not directly mentioned.
- Use Basic / Intermediate / Fluent / Native for language proficiency.
- Make sure the output is valid JSON without markdown, comments, or formatting.
"""





    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume parser that returns structured JSON and intelligently infers missing details."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
