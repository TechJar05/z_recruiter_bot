import fitz  # PyMuPDF
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from decouple import config
from openai import OpenAI
import re
from datetime import datetime
from dateutil import parser
import json


client = OpenAI(api_key=config("OPENAI_API_KEY"))
# Load the summarizer model once


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

        try:
            parsed_data = json.loads(parsed_data)
        except Exception:
            return Response({"error": "Failed to parse AI output"}, status=500)

        parsed_data = self.enrich_data(parsed_data, text)
        return Response({"parsed_resume": parsed_data})

    def extract_text(self, file):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join(page.get_text() for page in doc)

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
            return json.dumps({"error": str(e)})

    def enrich_data(self, data, raw_text):
        phone = str(data.get("contact_number", "")).replace(" ", "")
        address = data.get("residential_address", "").lower()
        pin = str(data.get("pin_code", ""))
        state_mentioned = any(state.lower() in address for state in INDIAN_STATES)

        # 1. Nationality inference
        nationality = ResumeParserAPIView.detect_nationality(phone)
        if nationality == "Indian" or state_mentioned:
            data["nationality"] = "Indian"
        else:
            data["nationality"] = "Unknown"

        # 3. Extract all dates
        data["all_dates_found"] = sorted(list(set(re.findall(r'\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{4}\b', raw_text))))

        # 4. Job durations, gaps, employment
        work_ex = data.get("work_experience", [])
        durations = []
        date_ranges = []
        currently_employed = False

        for job in work_ex:
            start_raw = job.get("start_date")
            end_raw = job.get("end_date") or datetime.now().strftime("%Y")

            if end_raw.lower() in ['present', 'current', 'till date']:
                currently_employed = True
                end_raw = datetime.now().strftime("%Y-%m")

            try:
                sdate = parser.parse(start_raw)
                edate = parser.parse(end_raw)
                if edate < sdate:
                    sdate, edate = edate, sdate
                duration_years = (edate - sdate).days / 365.25
                durations.append(duration_years)
                date_ranges.append((sdate, edate))
            except Exception:
                continue

        if durations:
            max_dur = max(durations)
            min_dur = min(durations)
            data["longest_job_duration"] = f"{int(max_dur)} years" if max_dur >= 1 else f"{int(max_dur * 12)} months"
            data["shortest_job_duration"] = f"{int(min_dur)} years" if min_dur >= 1 else f"{int(min_dur * 12)} months"

        # 5. Career gaps
        career_gaps = []
        if date_ranges:
            date_ranges.sort(key=lambda x: x[0])
            for i in range(1, len(date_ranges)):
                prev_end = date_ranges[i - 1][1]
                curr_start = date_ranges[i][0]
                gap_days = (curr_start - prev_end).days
                gap_months = gap_days // 30
                if gap_months > 1:
                    if gap_months < 12:
                        gap_text = f"{gap_months} months gap between {prev_end.date()} and {curr_start.date()}"
                    else:
                        gap_years = gap_months // 12
                        rem_months = gap_months % 12
                        gap_text = f"{gap_years} years" + (f" {rem_months} months" if rem_months else "") + \
                                   f" gap between {prev_end.date()} and {curr_start.date()}"
                    career_gaps.append(gap_text)

        data["career_gaps"] = career_gaps
        data["is_currently_employed"] = currently_employed

        # 6. Missing fields
        required_fields = [
            "full_name", "contact_number", "email_address", "resume_summary",
            "work_experience", "education", "technical_skills"
        ]
        data["missing_fields"] = [field for field in required_fields if not data.get(field)]
        data = ResumeParserAPIView.enrich_address_with_pincode(data, raw_text)

                # 7. Auto-generate work_summary and resume_summary if missing
       


        return data
    
    @staticmethod
    def detect_nationality(phone_number: str) -> str:
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, phone_number))

        # Handle numbers starting with country code +91 or local 10-digit numbers
        if digits.startswith('91') and len(digits) == 12:
            return "Indian"
        elif len(digits) == 10 and digits[0] in "6789":
            return "Indian"
        
        # Add more country patterns if needed
        return "Unknown"


    @staticmethod
    def correct_mumbai_pincode(pincode: str) -> str:
    # Known Mumbai last-3-digit endings
        mumbai_pincode_suffixes = {
            "001", "002", "003", "004", "005", "006", "007", "008", "009",
            "010", "011", "012", "013", "014", "015", "016", "017", "018", "019",
            "020", "021", "022", "023", "024", "025", "026", "027", "028", "029",
            "030", "031", "032", "033", "034", "035", "036", "037", "038", "039",
            "040", "041", "042", "043", "044", "045", "046", "047", "048", "049",
            "050", "051", "052", "053", "054", "055", "056", "057", "058", "059",
            "060", "061", "062", "063", "064", "065", "066", "067", "068", "069",
            "070", "071", "072", "073", "074", "075", "076", "077", "078", "079",
            "080", "081", "082", "083", "084", "085", "086", "087", "088", "089",
            "090", "091", "092", "093", "094", "095", "096", "097", "098", "099",
            "100", "104"
        }

        if len(pincode) == 3 and pincode in mumbai_pincode_suffixes:
            return "400" + pincode
        elif len(pincode) == 6:
            return pincode
        return ""
   
    @staticmethod
    def enrich_address_with_pincode(parsed_resume: dict, resume_text: str) -> dict:
        original_pincode = parsed_resume.get("pin_code", "")
        corrected_pincode = ResumeParserAPIView.correct_mumbai_pincode(original_pincode)

        if corrected_pincode:
            parsed_resume["pin_code"] = corrected_pincode
            # address = parsed_resume.get("address", "")
            address = parsed_resume.get("residential_address", "").strip()
            if corrected_pincode not in address:
                # parsed_resume["address"] = f"{address}, {corrected_pincode}".strip(", ")
                parsed_resume["residential_address"] = f"{address}, {corrected_pincode}".strip(", ")
        
        return parsed_resume

 