

# generate resume and work summery

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .services.ai_extractor import generate_individual_work_summaries, regenerate_resume_summary

class RegenerateSummaryAPIView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        summary_type = request.data.get('type')  # 'resume' or 'work'

        # Dynamically pick the right field
        if summary_type == 'resume':
            input_text = request.data.get('resume_summary')
        elif summary_type == 'work':
            input_text = request.data.get('work_summary')
        else:
            return Response({"error": "Invalid summary type"}, status=400)

        if not input_text:
            return Response({"error": f"{summary_type}_summary is required"}, status=400)

        trimmed_text = trimmed_text

        regenerated = regenerate_resume_summary(trimmed_text, summary_type)

        return Response({
            "type": summary_type,
            "regenerated_summary": regenerated
        })










# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from rest_framework import status
# import concurrent.futures
# import requests
# from django.conf import settings

# from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
# from .services.ai_extractor import extract_resume_data_with_ai, regenerate_resume_summary
# from .services.enrichers import enrich_resume_data
# from parser_app.utils.address_helpers import get_pincode_by_city
# from parser_app.utils.gender_utils import get_final_gender
# from parser_app.utils.linkedin_utils import normalize_linkedin_url  # optional helper to clean LinkedIn URL

# APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'


# class ResumeParserAPIView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         files = request.FILES.getlist('resume')
#         manual_linkedin_url = request.data.get("linkedin_url", "").strip()

#         if not files and not manual_linkedin_url:
#             return Response({"error": "No resumes uploaded or linkedin_url provided."}, status=400)

#         def process_resume(file):
#             try:
#                 # Step 1: Extract raw text
#                 file.seek(0)
#                 raw_text = extract_text_from_pdf(file)

#                 # Step 2: Extract profile image
#                 file.seek(0)
#                 profile_image = extract_images_from_pdf(file)

#                 # Step 3: AI resume parsing
#                 parsed_data = extract_resume_data_with_ai(raw_text)

#                 if parsed_data.get("work_experience"):
#                     parsed_data["work_experience_summaries"] = generate_individual_work_summaries(
#                         parsed_data["work_experience"],
#                         raw_text
#                     )

#                 # Step 4: Intelligent summary generation
#                 if not parsed_data.get("resume_summary"):
#                     parsed_data["resume_summary"] = regenerate_resume_summary(raw_text, "resume")
#                     parsed_data["resume_summary_generated"] = True
#                 else:
#                     parsed_data["resume_summary_generated"] = False

#                 if not parsed_data.get("work_summary"):
#                     parsed_data["work_summary"] = regenerate_resume_summary(raw_text, "work")
#                     parsed_data["work_summary_generated"] = True
#                 else:
#                     parsed_data["work_summary_generated"] = False

#                 # Step 5: Enrich parsed data
#                 enriched_data = enrich_resume_data(parsed_data, raw_text)

#                 # Step 6: Add gender if missing
#                 if not enriched_data.get("gender"):
#                     enriched_data["gender"] = get_final_gender(parsed_data.get("name", ""), raw_text)

#                 # Step 7: Add pincode if city is present
#                 city = enriched_data.get("city")
#                 if city and not enriched_data.get("pincode"):
#                     enriched_data["pincode"] = get_pincode_by_city(city)

#                 # Step 8: Attach profile image
#                 if profile_image:
#                     enriched_data["profile_image"] = profile_image["image_base64"]
#                     enriched_data["profile_image_meta"] = {
#                         "filename": profile_image["filename"],
#                         "width": profile_image["width"],
#                         "height": profile_image["height"],
#                         "page": profile_image["page"],
#                     }

#                 # Step 9: Determine LinkedIn URL (from resume or manual input)
#                 linkedin_url = (normalize_linkedin_url(parsed_data.get("linkedin_profile")) or manual_linkedin_url.strip())

#                 # Step 10: Fetch LinkedIn data from Apollo
#                 linkedin_data = None
#                 if linkedin_url:
#                     headers = {"X-Api-Key": settings.APOLLO_API_KEY}
#                     params = {"linkedin_url": linkedin_url}
#                     try:
#                         resp = requests.get(APOLLO_BASE_URL, headers=headers, params=params, timeout=10)
#                         linkedin_data = resp.json() if resp.status_code == 200 else {"error": resp.text}

#                         # if "person" in raw_linkedin_data:
#                         #     person = raw_linkedin_data["person"]
#                         #     linkedin_data = {
#                         #         "id": person.get("id"),
#                         #         "first_name": person.get("first_name"),
#                         #         "last_name": person.get("last_name"),
#                         #         "name": person.get("name"),
#                         #         "linkedin_url": person.get("linkedin_url"),
#                         #         "title": person.get("title"),
#                         #         "headline": person.get("headline"),
#                         #         "email": person.get("email"),
#                         #         "email_status": person.get("email_status"),
#                         #         "photo_url": person.get("photo_url"),
#                         #         "employment_history": person.get("employment_history"),
#                         #         "city": person.get("city"),
#                         #         "state": person.get("state"),
#                         #         "country": person.get("country"),
#                         #         "organization_id": person.get("organization_id"),
#                         #         "seniority": person.get("seniority")
#                         #     }
#                         # else:
#                         #     linkedin_data = raw_linkedin_data
#                     except Exception as e:
#                         linkedin_data = {"error": str(e)}


#                 enriched_data["linkedin_data"] = linkedin_data
#                 enriched_data["linkedin_url_used"] = linkedin_url

#                 return {"filename": file.name, "parsed_resume": enriched_data}

#             except Exception as e:
#                 return {"filename": file.name, "error": str(e)}

#         # Step 11: Parallel processing
#         with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#             results = list(executor.map(process_resume, files))

#         return Response({"results": results})




from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import concurrent.futures
import threading
import requests
from django.conf import settings

from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city
from parser_app.utils.gender_utils import get_final_gender
from parser_app.utils.linkedin_utils import normalize_linkedin_url

APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'


class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist('resume')
        manual_linkedin_url = request.data.get("linkedin_url", "").strip()

        if not files and not manual_linkedin_url:
            return Response({"error": "No resumes uploaded or linkedin_url provided."}, status=400)

        def process_resume(file):
            try:
                # 1️⃣ Extract raw text
                file.seek(0)
                raw_text = extract_text_from_pdf(file)

                # 2️⃣ Extract profile image (optional)
                file.seek(0)
                profile_image = extract_images_from_pdf(file)

                # 3️⃣ AI parsing + generate all job summaries in one call
                parsed_data = extract_resume_data_with_ai(raw_text)

                if parsed_data.get("work_experience"):
                    parsed_data["work_experience_summaries"] = generate_individual_work_summaries(
                        parsed_data["work_experience"],
                        raw_text
                    )



                # 4️⃣ Enrich parsed data
                enriched_data = enrich_resume_data(parsed_data, raw_text)

                # 5️⃣ Add gender if missing
                if not enriched_data.get("gender"):
                    enriched_data["gender"] = get_final_gender(parsed_data.get("full_name", ""), raw_text)

                # 6️⃣ Add pincode if city is present
                city = enriched_data.get("city")
                if city and not enriched_data.get("pin_code"):
                    enriched_data["pin_code"] = get_pincode_by_city(city)

                # 7️⃣ Attach profile image
                if profile_image:
                    enriched_data["profile_image"] = profile_image["image_base64"]
                    enriched_data["profile_image_meta"] = {
                        "filename": profile_image["filename"],
                        "width": profile_image["width"],
                        "height": profile_image["height"],
                        "page": profile_image["page"],
                    }

                # 8️⃣ Determine LinkedIn URL (resume or manual input)
                linkedin_raw = parsed_data.get("linkedin_profile") or manual_linkedin_url
                linkedin_url = normalize_linkedin_url(linkedin_raw)
                enriched_data["linkedin_url_used"] = linkedin_url

                # 9️⃣ Fetch LinkedIn data async
                linkedin_data = {}

                def fetch_linkedin():
                    nonlocal linkedin_data
                    if linkedin_url:
                        try:
                            headers = {"X-Api-Key": settings.APOLLO_API_KEY}
                            resp = requests.get(APOLLO_BASE_URL, headers=headers, params={"linkedin_url": linkedin_url}, timeout=10)
                            linkedin_data = resp.json() if resp.status_code == 200 else {"error": resp.text}
                        except Exception as e:
                            linkedin_data = {"error": str(e)}

                t = threading.Thread(target=fetch_linkedin)
                t.start()

                # 10️⃣ Return result immediately; LinkedIn data can attach later if needed
                result = {"filename": file.name, "parsed_resume": enriched_data, "linkedin_data": linkedin_data}

                # Optionally wait for LinkedIn thread if you want it included immediately
                t.join(timeout=5)
                result["linkedin_data"] = linkedin_data  # update if thread finished

                return result

            except Exception as e:
                return {"filename": file.name, "error": str(e)}

        # 11️⃣ Process multiple resumes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(process_resume, files))

        return Response({"results": results})
