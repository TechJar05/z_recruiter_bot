from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai, regenerate_resume_summary
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city 
from parser_app.utils.gender_utils import get_final_gender
from parser_app.utils.token_limiter import truncate_text
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser


class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('resume')
        if not file:
            return Response({"error": "No resume uploaded."}, status=400)

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

        return Response({"parsed_resume": enriched_data})






# views.py

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























# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
# from .services.ai_extractor import extract_resume_data_with_ai, regenerate_resume_summary
# from .services.enrichers import enrich_resume_data
# from parser_app.utils.address_helpers import get_pincode_by_city
# from parser_app.utils.gender_utils import get_final_gender
# from parser_app.utils.token_limiter import truncate_text

# import io

# class ResumeParserAPIView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         files = request.FILES.getlist('resume')  # support multiple files using key "resumes"
#         if not files:
#             return Response({"error": "No resumes uploaded."}, status=400)

#         results = []

#         # Worker function to process a single resume
#         def process_resume(file):
#             file_bytes = file.read()
#             file_io1 = io.BytesIO(file_bytes)
#             file_io2 = io.BytesIO(file_bytes)

#             # Step 1: Extract raw text
#             raw_text = extract_text_from_pdf(file_io1)

#             # Step 2: Extract profile image
#             profile_image = extract_images_from_pdf(file_io2)

#             # Step 3: Truncate long text
#             trimmed_text = truncate_text(raw_text)

#             # Step 4: AI resume parsing
#             parsed_data = extract_resume_data_with_ai(trimmed_text)

#             # Step 5: Intelligent summary generation
#             if not parsed_data.get("resume_summary"):
#                 parsed_data["resume_summary"] = regenerate_resume_summary(trimmed_text, "resume")
#                 parsed_data["resume_summary_generated"] = True
#             else:
#                 parsed_data["resume_summary_generated"] = False

#             if not parsed_data.get("work_summary"):
#                 parsed_data["work_summary"] = regenerate_resume_summary(trimmed_text, "work")
#                 parsed_data["work_summary_generated"] = True
#             else:
#                 parsed_data["work_summary_generated"] = False

#             # Step 6: Enrich data
#             enriched_data = enrich_resume_data(parsed_data, trimmed_text)

#             # Step 6.1: Add gender
#             if not enriched_data.get("gender"):
#                 enriched_data["gender"] = get_final_gender(parsed_data.get("name", ""), trimmed_text)

#             # Step 6.2: Add pincode
#             city = enriched_data.get("city")
#             if city and not enriched_data.get("pincode"):
#                 enriched_data["pincode"] = get_pincode_by_city(city)

#             # Step 7: Attach profile image
#             if profile_image:
#                 enriched_data["profile_image"] = profile_image["image_base64"]
#                 enriched_data["profile_image_meta"] = {
#                     "filename": profile_image["filename"],
#                     "width": profile_image["width"],
#                     "height": profile_image["height"],
#                     "page": profile_image["page"],
#                 }

#             return {"filename": file.name, "parsed_resume": enriched_data}

#         # Run all resumes in parallel using ThreadPoolExecutor
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             future_to_file = {executor.submit(process_resume, f): f for f in files}
#             for future in as_completed(future_to_file):
#                 try:
#                     result = future.result()
#                     results.append(result)
#                 except Exception as e:
#                     results.append({"filename": future_to_file[future].name, "error": str(e)})

#         return Response({"results": results})
