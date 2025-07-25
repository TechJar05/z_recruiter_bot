from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .services.resume_parser import extract_text_from_pdf,extract_images_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city 
import json
from parser_app.utils.gender_utils import get_final_gender
from parser_app.utils.token_limiter import truncate_text


class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('resume')
        if not file:
            return Response({"error": "No resume uploaded."}, status=400)

        # Reset file read pointer
        file.seek(0)
        raw_text = extract_text_from_pdf(file)

        # Reset again for image extraction
        file.seek(0)
        profile_image = extract_images_from_pdf(file)

        # Truncate + AI parsing
        trimmed_text = truncate_text(raw_text)
        parsed_data = extract_resume_data_with_ai(trimmed_text)

        # Continue enrichment
        enriched_data = enrich_resume_data(parsed_data, trimmed_text)

        # Attach image if found
        if profile_image:
            enriched_data["profile_image"] = profile_image["image_base64"]
            enriched_data["profile_image_meta"] = {
                "filename": profile_image["filename"],
                "width": profile_image["width"],
                "height": profile_image["height"],
                "page": profile_image["page"],
            }

        return Response({"parsed_resume": enriched_data})
