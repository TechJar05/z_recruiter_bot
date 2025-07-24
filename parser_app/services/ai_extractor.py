from openai import OpenAI
from decouple import config
import json

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def extract_resume_data_with_ai(resume_text: str) -> dict:
    prompt = f"""
Given this resume text:

{resume_text}

Extract this data in JSON:

{{
  "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "", "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",
  "resume_summary": "", "key_achievements": "",
  "work_experience": [{{"company_name": "", "start_date": "", "end_date": "", "industry": "", "designation": "", "department": ""}}],
  "education": [{{"degree": "", "institution_name": "", "year_of_passing": "", "grade": ""}}],
  "certifications": [{{"course_name": "", "platform": "", "certification_url": ""}}],
  "technical_skills": [], "soft_skills": [], "languages_known": [], "software_tools": [],
  "awards": [{{"year": "", "context": ""}}],
  "linkedin_profile": "", "github_link": "", "personal_website": "", "expected_salary": "", "current_salary": ""
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
