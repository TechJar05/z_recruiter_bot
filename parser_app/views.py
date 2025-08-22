


# views.py (or wherever your APIViews live)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
# from .services.ai_extractor import generate_individual_work_summaries, regenerate_resume_summary


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




# class ResumeParserAPIView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         files = request.FILES.getlist('resume')
#         manual_linkedin_url = request.data.get("linkedin_url", "").strip()

#         if not files and not manual_linkedin_url:
#             return Response({"error": "No resumes uploaded or linkedin_url provided."}, status=400)

#         def process_resume(file):
#             try:
#                 # 1) Extract raw text
#                 file.seek(0)
#                 raw_text = extract_text_from_pdf(file)

#                 # 2) Extract profile image (optional)
#                 file.seek(0)
#                 profile_image = extract_images_from_pdf(file)

#                 # 3) AI parsing
#                 parsed_data = extract_resume_data_with_ai(raw_text)

#                 # If AI parsing errored, return early for this file
#                 if isinstance(parsed_data, dict) and parsed_data.get("error"):
#                     return {"filename": file.name, "error": parsed_data["error"]}

                

#                 # 4) Enrich parsed data
#                 enriched_data = enrich_resume_data(parsed_data, raw_text)

#                 # 5) Add gender if missing
#                 if not enriched_data.get("gender"):
#                     enriched_data["gender"] = get_final_gender(parsed_data.get("full_name", ""), raw_text)

#                 # 6) Add pincode if city is present
#                 city = enriched_data.get("city")
#                 if city and not enriched_data.get("pin_code"):
#                     enriched_data["pin_code"] = get_pincode_by_city(city)

#                 # 7) Attach profile image
#                 if profile_image:
#                     enriched_data["profile_image"] = profile_image["image_base64"]
#                     enriched_data["profile_image_meta"] = {
#                         "filename": profile_image["filename"],
#                         "width": profile_image["width"],
#                         "height": profile_image["height"],
#                         "page": profile_image["page"],
#                     }

#                 # 8) Determine LinkedIn URL (resume or manual input)
#                 linkedin_raw = parsed_data.get("linkedin_profile") or manual_linkedin_url
#                 linkedin_url = normalize_linkedin_url(linkedin_raw)
#                 enriched_data["linkedin_url_used"] = linkedin_url

#                 # 9) Fetch LinkedIn data async (same as your code)
#                 linkedin_data = {}

#                 def fetch_linkedin():
#                     nonlocal linkedin_data
#                     if linkedin_url:
#                         try:
#                             headers = {"X-Api-Key": settings.APOLLO_API_KEY}
#                             resp = requests.get(
#                                 APOLLO_BASE_URL,
#                                 headers=headers,
#                                 params={"linkedin_url": linkedin_url},
#                                 timeout=10
#                             )
#                             linkedin_data = resp.json() if resp.status_code == 200 else {"error": resp.text}
#                         except Exception as e:
#                             linkedin_data = {"error": str(e)}

#                 t = threading.Thread(target=fetch_linkedin)
#                 t.start()

#                 # 10) Compose result (optionally wait briefly for LinkedIn)
#                 result = {"filename": file.name, "parsed_resume": enriched_data, "linkedin_data": linkedin_data}
#                 t.join(timeout=5)
#                 result["linkedin_data"] = linkedin_data

#                 return result

#             except Exception as e:
#                 return {"filename": getattr(file, 'name', 'unknown'), "error": str(e)}

#         # 11) Process multiple resumes in parallel (unchanged)
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#             results = list(executor.map(process_resume, files))

#         return Response({"results": results})





import concurrent.futures
import threading
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import io

class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist("resume")
        manual_linkedin_url = request.data.get("linkedin_url", "").strip()

        if not files and not manual_linkedin_url:
            return Response(
                {"error": "No resumes uploaded or linkedin_url provided."}, status=400
            )

        def process_resume(file):
            try:
                # Read file once into memory
                file_bytes = file.read()

                def get_text():
                    return extract_text_from_pdf(io.BytesIO(file_bytes))

                def get_image():
                    return extract_images_from_pdf(io.BytesIO(file_bytes))

                def get_ai(raw_text):
                    return extract_resume_data_with_ai(raw_text)

                # Step 1: run text + image in parallel
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                    future_text = ex.submit(get_text)
                    future_image = ex.submit(get_image)

                    raw_text = future_text.result()
                    profile_image = future_image.result()

                    # Step 2: run AI parsing + enrichment + gender + pincode in parallel
                    future_ai = ex.submit(get_ai, raw_text)

                    parsed_data = future_ai.result()
                    if isinstance(parsed_data, dict) and parsed_data.get("error"):
                        return {"filename": file.name, "error": parsed_data["error"]}

                    # Enrichment tasks (parallelize enrichment steps)
                    def enrich():
                        return enrich_resume_data(parsed_data, raw_text)

                    def detect_gender():
                        return get_final_gender(parsed_data.get("full_name", ""), raw_text)

                    def find_pincode(city):
                        return get_pincode_by_city(city) if city else None

                    future_enrich = ex.submit(enrich)
                    enriched_data = future_enrich.result()

                    # Gender & pincode async
                    future_gender = ex.submit(detect_gender)
                    future_pincode = ex.submit(find_pincode, enriched_data.get("city"))

                    if not enriched_data.get("gender"):
                        enriched_data["gender"] = future_gender.result()

                    if enriched_data.get("city") and not enriched_data.get("pin_code"):
                        enriched_data["pin_code"] = future_pincode.result()

                    # Attach profile image
                    if profile_image:
                        enriched_data["profile_image"] = profile_image["image_base64"]
                        enriched_data["profile_image_meta"] = {
                            "filename": profile_image["filename"],
                            "width": profile_image["width"],
                            "height": profile_image["height"],
                            "page": profile_image["page"],
                        }

                    # LinkedIn normalization
                    linkedin_raw = parsed_data.get("linkedin_profile") or manual_linkedin_url
                    linkedin_url = normalize_linkedin_url(linkedin_raw)
                    enriched_data["linkedin_url_used"] = linkedin_url

                    # Step 3: LinkedIn fetch (background, non-blocking)
                    linkedin_data = {}

                    def fetch_linkedin():
                        nonlocal linkedin_data
                        if linkedin_url:
                            try:
                                headers = {"X-Api-Key": settings.APOLLO_API_KEY}
                                resp = requests.get(
                                    APOLLO_BASE_URL,
                                    headers=headers,
                                    params={"linkedin_url": linkedin_url},
                                    timeout=10,
                                )
                                linkedin_data.update(
                                    resp.json()
                                    if resp.status_code == 200
                                    else {"error": resp.text}
                                )
                            except Exception as e:
                                linkedin_data.update({"error": str(e)})

                    threading.Thread(target=fetch_linkedin, daemon=True).start()

                    return {
                        "filename": file.name,
                        "parsed_resume": enriched_data,
                        "linkedin_data": linkedin_data,  # may still be empty immediately
                    }

            except Exception as e:
                return {"filename": getattr(file, "name", "unknown"), "error": str(e)}

        # Process all resumes concurrently
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {executor.submit(process_resume, f): f for f in files}
            for future in concurrent.futures.as_completed(future_to_file):
                results.append(future.result())

        return Response({"results": results})


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

        # ✅ fix the bug + trim overly long inputs for faster LLM latency
        trimmed_text = (input_text or "").strip()[:4000]

        regenerated = regenerate_resume_summary(trimmed_text, summary_type)

        return Response({
            "type": summary_type,
            "regenerated_summary": regenerated
        })

