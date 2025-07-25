# import fitz  # PyMuPDF
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from decouple import config
# from openai import OpenAI


# from decouple import config
# from openai import OpenAI

# client = OpenAI(api_key=config("OPENAI_API_KEY"))

# import os
# class ResumeParserAPIView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         file = request.FILES.get('resume')
#         if not file:
#             return Response({"error": "No resume uploaded."}, status=400)

#         text = self.extract_text(file)
#         parsed_data = self.ask_openai(text)
#         return Response({"parsed_resume": parsed_data})

#     def extract_text(self, file):
#         doc = fitz.open(stream=file.read(), filetype="pdf")
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         return text

#     def ask_openai(self, text):
       

#         prompt = f"""
# Given this resume text:

# {text}

# Extract this data in JSON:

# {{
#   "full_name": "", "contact_number": "", "email_address": "", "date_of_birth": "", "gender": "", "marital_status": "", "nationality": "", "residential_address": "", "pin_code": "",
#   "resume_summary": "", "key_achievements": "",
#   "work_experience": [{{"company_name": "", "start_date": "", "end_date": "", "industry": "", "designation": "", "department": ""}}],
#   "education": [{{"degree": "", "institution_name": "", "year_of_passing": "", "grade": ""}}],
#   "certifications": [{{"course_name": "", "platform": "", "certification_url": ""}}],
#   "technical_skills": [], "soft_skills": [], "languages_known": [], "software_tools": [],
#   "awards": [{{"year": "", "context": ""}}],
#   "linkedin_profile": "", "github_link": "", "personal_website": "", "expected_salary": "", "current_salary": ""
# }}
# """

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a professional resume parser."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=2000
#             )
#             return response.choices[0].message.content
#         except Exception as e:
#             return {"error": str(e)}


import fitz  # PyMuPDF
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from decouple import config
from openai import OpenAI


from decouple import config
from openai import OpenAI

client = OpenAI(api_key=config("OPENAI_API_KEY"))

import os
class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('resume')
        if not file:
            return Response({"error": "No resume uploaded."}, status=400)

        text = self.extract_text(file)
        parsed_data = self.ask_openai(text)
        return Response({"parsed_resume": parsed_data})

    def extract_text(self, file):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def ask_openai(self, text):
       

        prompt = f"""
Given this resume text:

{text}

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
            return response.choices[0].message.content
        except Exception as e:
            return {"error": str(e)}
        












import fitz  # PyMuPDF
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from decouple import config
from openai import OpenAI


from decouple import config
from openai import OpenAI

client = OpenAI(api_key=config("OPENAI_API_KEY"))

import os


import re
from datetime import datetime

INDIAN_STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Rajasthan", "Kerala", "Punjab", "Delhi",
    "Uttar Pradesh", "West Bengal", "Bihar", "Telangana", "Andhra Pradesh", "Madhya Pradesh", "Odisha"
]




class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    
    def post(self, request):
        file = request.FILES.get('resume')
        if not file:
            return Response({"error": "No resume uploaded."}, status=400)

        text = self.extract_text(file)
        parsed_data = self.ask_openai(text)
        
        # Try parsing string to dict (OpenAI returns a string JSON)
        try:
            import json
            parsed_data = json.loads(parsed_data)
        except:
            return Response({"error": "Failed to parse AI output"}, status=500)

        # Post-processing
        parsed_data = self.enrich_data(parsed_data, text)

        return Response({"parsed_resume": parsed_data})


    

    def extract_text(self, file):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def ask_openai(self, text):
       

        prompt = f"""
Given this resume text:

{text}

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
            return response.choices[0].message.content
        except Exception as e:
            return {"error": str(e)}
     
    


    def enrich_data(self, data, raw_text):
    # 1. Nationality inference
        phone = data.get("contact_number", "")
        address = data.get("residential_address", "").lower()
        pin = data.get("pin_code", "")
        state_mentioned = any(state.lower() in address for state in INDIAN_STATES)

        if (re.match(r"(\+91\d{10}|\d{10})", phone) or state_mentioned):
            data["nationality"] = "Indian"

        # 2. Mumbai 3-digit pincode completion (assume 400xxx)
        if pin and len(pin) == 3 and address and "mumbai" in address:
            data["pin_code"] = "400" + pin

        # 3. All dates mentioned in resume
        dates_found = re.findall(r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{4}\b', raw_text)
        data["all_dates_found"] = list(set(dates_found))

        # 4. Career gap detection & job duration
        work_ex = data.get("work_experience", [])
        date_format_variants = ["%d-%m-%Y", "%d/%m/%Y", "%Y", "%m/%Y"]

        durations = []
        date_ranges = []

        for job in work_ex:
            start = job.get("start_date")
            end = job.get("end_date") or datetime.now().strftime("%Y")
            try:
                sdate = self.parse_date(start)
                edate = self.parse_date(end)
                diff_years = (edate - sdate).days / 365.25
                durations.append(diff_years)
                date_ranges.append((sdate, edate))
            except:
                continue

        if durations:
            data["longest_job_duration_years"] = round(max(durations), 2)
            data["shortest_job_duration_years"] = round(min(durations), 2)

        # Detect career gaps
        career_gaps = []
        date_ranges.sort()
        for i in range(1, len(date_ranges)):
            gap = (date_ranges[i][0] - date_ranges[i-1][1]).days / 30
            if gap > 6:  # gap > 6 months
                career_gaps.append(f"Gap of {int(gap)} months between {date_ranges[i-1][1].date()} and {date_ranges[i][0].date()}")

        data["career_gaps"] = career_gaps

        # 5. Detect missing required fields
        required_fields = [
            "full_name", "contact_number", "email_address", "resume_summary",
            "work_experience", "education", "technical_skills"
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        data["missing_fields"] = missing_fields

        return data
    

    def parse_date(self, date_str):
        from dateutil import parser
        return parser.parse(date_str)