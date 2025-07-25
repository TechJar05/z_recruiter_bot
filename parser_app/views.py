# Import the render function to render templates
from django.shortcuts import render

# Your existing imports
import fitz  # PyMuPDF
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from decouple import config
from openai import OpenAI
import requests
import os
import re
from datetime import datetime
import json

# OpenAI API client
client = OpenAI(api_key=config("OPENAI_API_KEY"))

# Indian states for enriching data
INDIAN_STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Rajasthan", "Kerala", "Punjab", "Delhi",
    "Uttar Pradesh", "West Bengal", "Bihar", "Telangana", "Andhra Pradesh", "Madhya Pradesh", "Odisha"
]

# LinkedIn Profile Model
from .models import LinkedInProfile

# View for rendering index.html (Place this after imports and before other views)
def index(request):
    return render(request, 'index.html')


# Resume parsing view (existing code)
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
        phone = data.get("contact_number", "")
        address = data.get("residential_address", "").lower()
        pin = data.get("pin_code", "")
        state_mentioned = any(state.lower() in address for state in INDIAN_STATES)

        if (re.match(r"(\+91\d{10}|\d{10})", phone) or state_mentioned):
            data["nationality"] = "Indian"

        if pin and len(pin) == 3 and address and "mumbai" in address:
            data["pin_code"] = "400" + pin

        dates_found = re.findall(r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{4}\b', raw_text)
        data["all_dates_found"] = list(set(dates_found))

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

        career_gaps = []
        date_ranges.sort()
        for i in range(1, len(date_ranges)):
            gap = (date_ranges[i][0] - date_ranges[i-1][1]).days / 30
            if gap > 6:
                career_gaps.append(f"Gap of {int(gap)} months between {date_ranges[i-1][1].date()} and {date_ranges[i][0].date()}")

        data["career_gaps"] = career_gaps

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


# ✅ New: LinkedIn OAuth Handler
@api_view(['POST'])
def linkedin_exchange_view(request):
    code = request.data.get("code")
    state = request.data.get("state")  # optional, use to identify the candidate

    if not code:
        return Response({"error": "Missing authorization code"}, status=400)

    # Step 1: Get Access Token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://www.rms.zecruiters.com/AI",
        "client_id": "77efxh74ei8t5n",
        "client_secret": "WPL_AP1.mzQLa3twcal4NqH"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post(token_url, data=payload, headers=headers)
    token_data = token_response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return Response({"error": "Failed to get access token", "details": token_data}, status=400)

    # Step 2: Fetch LinkedIn profile
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
    email_resp = requests.get(
        "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
        headers=headers
    ).json()

    email = email_resp["elements"][0]["handle~"]["emailAddress"]
    linkedin_id = profile.get("id")
    first_name = profile.get("localizedFirstName")
    last_name = profile.get("localizedLastName")

    # Step 3: Save or update in DB
    obj, created = LinkedInProfile.objects.get_or_create(
        linkedin_id=linkedin_id,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "state": state or "",
            "access_token": access_token,
            "profile_data": profile
        }
    )

    if not created:
        # Optionally update token or profile if already exists
        obj.access_token = access_token
        obj.profile_data = profile
        obj.save()

    return Response({
        "message": "✅ LinkedIn profile saved successfully",
        "data": {
            "linkedin_id": linkedin_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "state": state,
            "created": created
        }
    }, status=status.HTTP_200_OK)
