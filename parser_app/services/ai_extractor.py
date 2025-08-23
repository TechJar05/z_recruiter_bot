

# services/ai_extractor.py

from openai import OpenAI
from decouple import config
import json
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




def extract_resume_data_with_ai(resume_text: str) -> dict:
    prompt = f"""
Given this resume text:

{resume_text}

Extract the following structured data in valid JSON format. If any field is missing, infer it from context. If the data is not present or cannot be inferred, leave the value empty.


Rules for `industry`:
- Match strictly with one from this list:
{INDUSTRY_LIST}
- If no exact match is found, infer from context and append " (AI Inferred)".

Rules for `education`:
- Match strictly with one from this list:
{EDUCATION_LIST}
- If no exact match is found, infer from context and append " (AI Inferred)".

If any field is missing, infer it from context. 
If data cannot be inferred, leave it empty.


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
- "overall_work_summary" should summarize the candidate’s career across all jobs in 4–6 sentences.
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
            temperature=0.0,
            max_tokens=1500
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
