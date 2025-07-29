from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .services.resume_parser import extract_text_from_pdf, extract_images_from_pdf
from .services.ai_extractor import extract_resume_data_with_ai, regenerate_resume_summary
from .services.enrichers import enrich_resume_data
from parser_app.utils.address_helpers import get_pincode_by_city 
from parser_app.utils.gender_utils import get_final_gender
from parser_app.utils.token_limiter import truncate_text

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

        # Check if AI extraction failed
        if "error" in parsed_data:
            return Response({
                "error": "Resume parsing failed", 
                "details": parsed_data.get("details", "Unknown error"),
                "ai_response": parsed_data.get("ai_response", "")
            }, status=500)

        # Step 5: Intelligent summary generation
        if not parsed_data.get("resume_summary") or parsed_data.get("resume_summary") == "N/A":
            parsed_data["resume_summary"] = regenerate_resume_summary(trimmed_text, "resume")
            parsed_data["resume_summary_generated"] = True
        else:
            parsed_data["resume_summary_generated"] = False

        if not parsed_data.get("work_summary") or parsed_data.get("work_summary") == "N/A":
            parsed_data["work_summary"] = regenerate_resume_summary(trimmed_text, "work")
            parsed_data["work_summary_generated"] = True
        else:
            parsed_data["work_summary_generated"] = False

        # Step 6: Enrich the parsed data (includes fallback address extraction)
        enriched_data = enrich_resume_data(parsed_data, trimmed_text)

        # Step 6.1: Add gender if missing
        if not enriched_data.get("gender") or enriched_data.get("gender") == "N/A":
            enriched_data["gender"] = get_final_gender(parsed_data.get("full_name", ""), trimmed_text)

        # Step 6.2: Add pincode if city is present but pincode is missing
        city = enriched_data.get("city")
        if city and city != "N/A" and (not enriched_data.get("pincode") or enriched_data.get("pincode") == "N/A"):
            fetched_pincode = get_pincode_by_city(city)
            if fetched_pincode:
                enriched_data["pincode"] = fetched_pincode

        # Step 7: Attach profile image
        if profile_image:
            enriched_data["profile_image"] = profile_image["image_base64"]
            enriched_data["profile_image_meta"] = {
                "filename": profile_image["filename"],
                "width": profile_image["width"],
                "height": profile_image["height"],
                "page": profile_image["page"],
            }

        # Step 8: Log extraction results for debugging
        print("=== FINAL EXTRACTION RESULTS ===")
        print(f"Address: {enriched_data.get('address', 'N/A')}")
        print(f"City: {enriched_data.get('city', 'N/A')}")
        print(f"Pincode: {enriched_data.get('pin_code', 'N/A')}")
        print(f"Name: {enriched_data.get('full_name', 'N/A')}")
        print(f"Phone: {enriched_data.get('contact_number', 'N/A')}")

        return Response({"parsed_resume": enriched_data})