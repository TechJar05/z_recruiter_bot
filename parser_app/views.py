
import asyncio
import concurrent.futures
import threading
import requests
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework import status
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
        files = request.FILES.getlist("resume")
        manual_linkedin_url = request.data.get("linkedin_url", "").strip()

        if not files and not manual_linkedin_url:
            return Response(
                {"error": "No resumes uploaded or linkedin_url provided."}, status=400
            )

        async def process_resume(file):
            try:
                file_bytes = file.read()

                loop = asyncio.get_event_loop()

                # 1) Extract raw text
                raw_text = await loop.run_in_executor(None, extract_text_from_pdf, io.BytesIO(file_bytes))

                # 2) Extract profile image
                profile_image = await loop.run_in_executor(None, extract_images_from_pdf, io.BytesIO(file_bytes))

                # 3) AI parsing
                parsed_data = await loop.run_in_executor(None, extract_resume_data_with_ai, raw_text)

                if isinstance(parsed_data, dict) and parsed_data.get("error"):
                    return {"filename": file.name, "error": parsed_data["error"]}

                # 4) Enrich parsed data
                enriched_data = enrich_resume_data(parsed_data, raw_text)

                # 5) Add gender if missing
                if not enriched_data.get("gender"):
                    enriched_data["gender"] = get_final_gender(
                        parsed_data.get("full_name", ""), raw_text
                    )

                # 6) Add pincode if city is present
                city = enriched_data.get("city")
                if city and not enriched_data.get("pin_code"):
                    enriched_data["pin_code"] = get_pincode_by_city(city)

                # 7) Attach profile image
                if profile_image:
                    enriched_data["profile_image"] = profile_image["image_base64"]
                    enriched_data["profile_image_meta"] = {
                        "filename": profile_image["filename"],
                        "width": profile_image["width"],
                        "height": profile_image["height"],
                        "page": profile_image["page"],
                    }

                # 8) LinkedIn URL
                linkedin_raw = parsed_data.get("linkedin_profile") or manual_linkedin_url
                linkedin_url = normalize_linkedin_url(linkedin_raw)
                enriched_data["linkedin_url_used"] = linkedin_url

                # 9) Fetch LinkedIn data async (background thread)
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
                            linkedin_data = (
                                resp.json()
                                if resp.status_code == 200
                                else {"error": resp.text}
                            )
                        except Exception as e:
                            linkedin_data = {"error": str(e)}

                t = threading.Thread(target=fetch_linkedin)
                t.start()

                result = {
                    "filename": file.name,
                    "parsed_resume": enriched_data,
                    "linkedin_data": {},
                }

                # Wait up to 5s for LinkedIn
                t.join(timeout=5)
                result["linkedin_data"] = linkedin_data

                return result

            except Exception as e:
                return {"filename": getattr(file, "name", "unknown"), "error": str(e)}

        async def process_all():
            tasks = [process_resume(f) for f in files]
            return await asyncio.gather(*tasks)

        # ✅ Run async pipeline inside sync `post`
        results = asyncio.run(process_all())

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

