

# services/ai_extractor.py

from openai import OpenAI
from decouple import config
import json

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def extract_resume_data_with_ai(resume_text: str) -> dict:
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
- "industry" should reflect the primary domain: Inforamtion Technology, Finance, Healthcare, etc.
- "technical_skills" must include programming languages, libraries, frameworks, APIs.
- "software_tools" must include only actual software (e.g., VS Code, Git, JIRA, Postman).
- "functional_skills" are domain-level tasks (e.g., project management, analysis).
- "soft_skills" should be inferred (e.g., leadership, teamwork) if not directly mentioned.
- Use Basic / Intermediate / Fluent / Native for language proficiency.
- Make sure the output is valid JSON without markdown, comments, or formatting.
- Always expand degree abbreviations into their full forms (e.g., "B.Com" → "Bachelor of Commerce", "BE" → "Bachelor of Engineering", "BCA" → "Bachelor of Computer Applications", "MBA" → "Master of Business Administration", etc.).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
            temperature=0.2,
            max_tokens=1800
        )
        return json.loads(response.choices[0].message.content)
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
