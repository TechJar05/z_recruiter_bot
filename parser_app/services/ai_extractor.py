# from openai import OpenAI
# from decouple import config
# import json

# client = OpenAI(api_key=config("OPENAI_API_KEY"))

# def extract_resume_data_with_ai(resume_text: str) -> dict:

#     prompt = f"""
# Given this resume text:

# {resume_text}

# Extract the following structured data in valid JSON format. If any field is missing, infer it from context. If the data is not present or cannot be inferred, leave the value empty.

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
# - "industry" should reflect the primary domain: IT, Finance, Healthcare, etc.
# - "technical_skills" must include programming languages, libraries, frameworks, APIs.
# - "software_tools" must include only actual software (e.g., VS Code, Git, JIRA, Postman).
# - "functional_skills" are domain-level tasks (e.g., project management, analysis).
# - "soft_skills" should be inferred (e.g., leadership, teamwork) if not directly mentioned.
# - Use Basic / Intermediate / Fluent / Native for language proficiency.
# - Make sure the output is valid JSON without markdown, comments, or formatting.
# """





#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
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
#             temperature=0.3,
#             max_tokens=2000
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception as e:
#         return {"error": str(e)}





# import concurrent.futures

# def generate_individual_work_summaries(work_experience: list, resume_text: str):
#     from openai import OpenAI
#     from decouple import config

#     client = OpenAI(api_key=config("OPENAI_API_KEY"))

#     def generate(job):
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
#             return {"company_name": job.get("company_name", ""), "work_summary": response.choices[0].message.content.strip()}
#         except Exception as e:
#             return {"company_name": job.get("company_name", ""), "work_summary": f"Error: {str(e)}"}

#     # Parallel execution
#     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#         results = list(executor.map(generate, work_experience))

#     return results




# # ai_extractor.py
# def regenerate_resume_summary(resume_text: str, summary_type: str, prev_resume_summary: str = "", prev_work_summary: str = "") -> str:
#     from openai import OpenAI
#     from decouple import config

#     client = OpenAI(api_key=config("OPENAI_API_KEY"))

#     base_prompt = {
#         "resume": "Based on the resume text, previous resume summary, and work summary below, generate a clear, concise (3–5 sentences), and professional **resume summary**:",
#         "work": "Based on the resume text, previous resume summary, and work summary below, generate a clear, concise (3–5 sentences), and professional **work experience summary**:"
#     }

#     prompt = f"""{base_prompt[summary_type]}

# --- Resume Text ---
# {resume_text}

# --- Previous Resume Summary ---
# {prev_resume_summary or "Not available"}

# --- Previous Work Summary ---
# {prev_work_summary or "Not available"}

# Respond with a rewritten version that feels polished and optimized for professional use.
# """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an expert resume and career summary writer."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5,
#             max_tokens=500
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error generating summary: {str(e)}"
    







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


def generate_individual_work_summaries(work_experience: list, resume_text: str):
    """
    BATched version (same name!). Summarizes ALL jobs in ONE LLM call.
    Returns a list like: [{"index": 0, "company_name": "...", "work_summary": "..."}, ...]
    """
    try:
        if not work_experience:
            return []

        # Build a compact payload with indices to preserve order/mapping.
        jobs_payload = []
        for idx, job in enumerate(work_experience):
            jobs_payload.append({
                "index": idx,
                "company_name": job.get("company_name", ""),
                "designation": job.get("designation", ""),
                "department": job.get("department", ""),
                "start_date": job.get("start_date", ""),
                "end_date": job.get("end_date", "")
            })

        prompt = f"""
You are an expert career and resume writer.

Task:
- Given the resume text and the list of job experiences (with index), write a professional, concise (2–4 sentences) work summary for EACH job.
- The summary should be specific and reflect the role, impact, and skills.
- Return ONLY a valid JSON array. No extra text. No markdown.
- Each element must be: {{"index": <int>, "company_name": "<str>", "work_summary": "<str>"}}
- Keep the same 'index' as the input so we can map results back.

--- Resume Text ---
{resume_text}

--- Work Experiences (JSON) ---
{json.dumps(jobs_payload, ensure_ascii=False)}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=900
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        # Optional: sanity fallback if the model returns an object
        if isinstance(data, dict):
            data = [data]

        return data

    except Exception as e:
        return [{"error": str(e)}]


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
