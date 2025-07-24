

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .services.resume_parser import extract_text_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city 
import json

class ResumeParserAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('resume')
        if not file:
            return Response({"error": "No resume uploaded."}, status=400)

        raw_text = extract_text_from_pdf(file)
        parsed_data = extract_resume_data_with_ai(raw_text)

        if "error" in parsed_data:
            return Response({"error": parsed_data["error"]}, status=500)

        # Enrich the resume data first
        enriched_data = enrich_resume_data(parsed_data, raw_text)

        # Extra logic to append pincode if missing
        city = enriched_data.get("city")
        pincode = enriched_data.get("pin_code")
        address = enriched_data.get("residential_address")

        return Response({"parsed_resume": enriched_data})
