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
