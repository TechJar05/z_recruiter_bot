from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .services.resume_parser import extract_text_from_pdf
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

        raw_text = extract_text_from_pdf(file)
        trimmed_text = truncate_text(raw_text, max_chars=3000)
        parsed_data = extract_resume_data_with_ai(raw_text)

        if "error" in parsed_data:
            return Response({"error": parsed_data["error"]}, status=500)
        

            # --- Add Gender Detection ---
        name = parsed_data.get("name", "")
        gender = get_final_gender(name, raw_text)
        parsed_data["gender"] = gender

        # Step 1: Enrich data (e.g. gender, salary, etc.)
        enriched_data = enrich_resume_data(parsed_data, raw_text)

        # Step 2: If pincode is missing but city is available, try to fetch it
        if not enriched_data.get("pin_code") and enriched_data.get("city"):
            fetched_pincode = get_pincode_by_city(enriched_data["city"])
            if fetched_pincode:
                enriched_data["pin_code"] = fetched_pincode

        return Response({"parsed_resume": enriched_data})
