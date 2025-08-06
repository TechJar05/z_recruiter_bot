




from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai, regenerate_resume_summary
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city 
from parser_app.utils.gender_utils import get_final_gender
from parser_app.utils.token_limiter import truncate_text
import os
import concurrent.futures
import requests
from rest_framework import status



# resume parsing
class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist('resume')
        if not files:
            return Response({"error": "No resumes uploaded."}, status=400)

        def process_resume(file):
            try:
                # Step 1: Extract raw text
                file.seek(0)
                raw_text = extract_text_from_pdf(file)

                # Step 2: Extract profile image
                file.seek(0)
                profile_image = extract_images_from_pdf(file)

                # Step 3: Truncate long text
                trimmed_text = truncate_text(raw_text)

                # Step 4: AI resume parsing
                parsed_data = extract_resume_data_with_ai(trimmed_text)

                # Step 5: Intelligent summary generation
                if not parsed_data.get("resume_summary"):
                    parsed_data["resume_summary"] = regenerate_resume_summary(trimmed_text, "resume")
                    parsed_data["resume_summary_generated"] = True
                else:
                    parsed_data["resume_summary_generated"] = False

                if not parsed_data.get("work_summary"):
                    parsed_data["work_summary"] = regenerate_resume_summary(trimmed_text, "work")
                    parsed_data["work_summary_generated"] = True
                else:
                    parsed_data["work_summary_generated"] = False

                # Step 6: Enrich the parsed data
                enriched_data = enrich_resume_data(parsed_data, trimmed_text)

                # Step 6.1: Add gender if missing
                if not enriched_data.get("gender"):
                    enriched_data["gender"] = get_final_gender(parsed_data.get("name", ""), trimmed_text)

                # Step 6.2: Add pincode if city is present
                city = enriched_data.get("city")
                if city and not enriched_data.get("pincode"):
                    enriched_data["pincode"] = get_pincode_by_city(city)

                # Step 7: Attach profile image
                if profile_image:
                    enriched_data["profile_image"] = profile_image["image_base64"]
                    enriched_data["profile_image_meta"] = {
                        "filename": profile_image["filename"],
                        "width": profile_image["width"],
                        "height": profile_image["height"],
                        "page": profile_image["page"],
                    }

                return {"filename": file.name, "parsed_resume": enriched_data}
            except Exception as e:
                return {"filename": file.name, "error": str(e)}

        # Step 8: Parallel processing using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(process_resume, files))

        return Response({"results": results})



# generate resume and work summery

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .services.ai_extractor import regenerate_resume_summary
from parser_app.utils.token_limiter import truncate_text

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

        trimmed_text = truncate_text(input_text)

        regenerated = regenerate_resume_summary(trimmed_text, summary_type)

        return Response({
            "type": summary_type,
            "regenerated_summary": regenerated
        })





# # # linkedin parsing
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os
from django.conf import settings

APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'


class ApolloLinkedInLookupAPIView(APIView):
    def post(self, request):
        linkedin_url = request.data.get("linkedin_url")

        if not linkedin_url:
            return Response({"error": "linkedin_url is required"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"X-Api-Key":settings.APOLLO_API_KEY}
        params = {"linkedin_url": linkedin_url}

        try:
            apollo_response = requests.get(APOLLO_BASE_URL, headers=headers, params=params)

            try:
                data = apollo_response.json()
            except ValueError:
                return Response({
                    "error": "Apollo API did not return valid JSON.",
                    "status_code": apollo_response.status_code,
                    "raw_response": apollo_response.text  # helpful for debugging
                }, status=apollo_response.status_code)

            return Response(data, status=apollo_response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







# with word document

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# import os
# from django.conf import settings
# from docx import Document
# from docx.shared import Inches
# from io import BytesIO

# APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'

# class ApolloLinkedInLookupAPIView(APIView):
#     def post(self, request):
#         linkedin_url = request.data.get("linkedin_url")

#         if not linkedin_url:
#             return Response({"error": "linkedin_url is required"}, status=status.HTTP_400_BAD_REQUEST)

#         headers = {"X-Api-Key": settings.APOLLO_API_KEY}
#         params = {"linkedin_url": linkedin_url}

#         try:
#             apollo_response = requests.get(APOLLO_BASE_URL, headers=headers, params=params)

#             try:
#                 data = apollo_response.json()
#             except ValueError:
#                 return Response({
#                     "error": " API did not return valid JSON.",
#                     "status_code": apollo_response.status_code,
#                     "raw_response": apollo_response.text
#                 }, status=apollo_response.status_code)

#             # Save formatted response to Word doc
#             self.save_response_to_word(data)

#             return Response(data, status=apollo_response.status_code)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def save_response_to_word(self, data):
#         document = Document()
#         document.add_heading(' LinkedIn Lookup Result', 0)

#         person_data = data.get("person", {})
#         enriched_data = data.get("enrichment", {})

#         # Add photo if exists
#         photo_url = person_data.get("photo_url") or enriched_data.get("photo_url")
#         if photo_url:
#             try:
#                 image_response = requests.get(photo_url)
#                 if image_response.status_code == 200:
#                     image_stream = BytesIO(image_response.content)
#                     document.add_picture(image_stream, width=Inches(1.5))
#             except:
#                 pass

#         # Format nested data
#         def write_data(section_title, data_dict):
#             document.add_heading(section_title, level=1)
#             for key, value in data_dict.items():
#                 if isinstance(value, list):
#                     document.add_paragraph(f"{key}:", style='List Bullet')
#                     for item in value:
#                         if isinstance(item, dict):
#                             for sub_key, sub_value in item.items():
#                                 document.add_paragraph(f"  {sub_key}: {sub_value}", style='List Bullet 2')
#                         else:
#                             document.add_paragraph(f"  - {item}", style='List Bullet 2')
#                 elif isinstance(value, dict):
#                     document.add_paragraph(f"{key}:", style='List Bullet')
#                     for sub_key, sub_value in value.items():
#                         document.add_paragraph(f"  {sub_key}: {sub_value}", style='List Bullet 2')
#                 else:
#                     document.add_paragraph(f"{key}: {value}", style='List Bullet')

#         if person_data:
#             write_data("Basic Information", person_data)

#         if enriched_data:
#             write_data("Enriched Information", enriched_data)

#         file_name = person_data.get("name", "apollo_result").replace(" ", "_") + ".docx"
#         save_path = os.path.join(settings.BASE_DIR, "apollo_exports", file_name)

#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         document.save(save_path)
