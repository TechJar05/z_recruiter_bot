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







# ai_extractor.py
def regenerate_resume_summary(resume_text: str, summary_type: str, prev_resume_summary: str = "", prev_work_summary: str = "") -> str:
    from openai import OpenAI
    from decouple import config

    client = OpenAI(api_key=config("OPENAI_API_KEY"))

    base_prompt = {
        "resume": "Based on the resume text, previous resume summary, and work summary below, generate a clear, concise (3–5 sentences), and professional **resume summary**:",
        "work": "Based on the resume text, previous resume summary, and work summary below, generate a clear, concise (3–5 sentences), and professional **work experience summary**:"
    }

    prompt = f"""{base_prompt[summary_type]}

--- Resume Text ---
{resume_text}

--- Previous Resume Summary ---
{prev_resume_summary or "Not available"}

--- Previous Work Summary ---
{prev_work_summary or "Not available"}

Respond with a rewritten version that feels polished and optimized for professional use.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume and career summary writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"
    


import concurrent.futures

def generate_individual_work_summaries(work_experience: list, resume_text: str):
    from openai import OpenAI
    from decouple import config

    client = OpenAI(api_key=config("OPENAI_API_KEY"))

    def generate(job):
        job_prompt = f"""
Based on the resume text and this specific job experience, generate a professional, concise (2-4 sentences) work summary.

--- Resume Text ---
{resume_text}

--- Job Details ---
Company: {job.get("company_name", "")}
Designation: {job.get("designation", "")}
Department: {job.get("department", "")}
Start Date: {job.get("start_date", "")}
End Date: {job.get("end_date", "")}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career and resume writer."},
                    {"role": "user", "content": job_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            return {"company_name": job.get("company_name", ""), "work_summary": response.choices[0].message.content.strip()}
        except Exception as e:
            return {"company_name": job.get("company_name", ""), "work_summary": f"Error: {str(e)}"}

    # Parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(generate, work_experience))

    return results


  




# def generate_individual_work_summaries(work_experience: list, resume_text: str) -> list:
#     """
#     Generates a polished work summary for each job in the work_experience list.
#     """
#     from openai import OpenAI
#     from decouple import config

#     client = OpenAI(api_key=config("OPENAI_API_KEY"))
#     job_summaries = []

#     for job in work_experience:
#         # Compose a job-specific prompt
#         job_prompt = f"""
# Based on the resume text and this specific job experience, generate a professional, concise (2-4 sentences) work summary.

# --- Resume Text ---
# {resume_text}

# --- Job Details ---
# Company: {job.get("company_name", "")}
# Designation: {job.get("designation", "")}
# Department: {job.get("department", "")}
# Start Date: {job.get("start_date", "")}
# End Date: {job.get("end_date", "")}

# Respond with a polished work summary suitable for LinkedIn or resume.
# """

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are an expert career and resume writer."},
#                     {"role": "user", "content": job_prompt}
#                 ],
#                 temperature=0.5,
#                 max_tokens=200
#             )
#             job_summary = response.choices[0].message.content.strip()
#         except Exception as e:
#             job_summary = f"Error generating summary: {str(e)}"

#         job_summaries.append({"company_name": job.get("company_name", ""), "work_summary": job_summary})

#     return job_summaries
