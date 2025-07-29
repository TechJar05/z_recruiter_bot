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

        # Step 4.1: Field mapping consistency fix
        # Ensure that both 'address' and 'residential_address' fields are properly mapped
        if parsed_data.get("address") and not parsed_data.get("residential_address"):
            parsed_data["residential_address"] = parsed_data["address"]
        elif parsed_data.get("residential_address") and not parsed_data.get("address"):
            parsed_data["address"] = parsed_data["residential_address"]

        # Also handle city field mapping
        if not parsed_data.get("city"):
            # Try to extract city from address for pincode lookup
            address = parsed_data.get("residential_address", "")
            if address and address != "N/A":
                # Simple city extraction - you might want to improve this
                import re
                # Look for common Indian city patterns
                indian_cities = [
                    "mumbai", "delhi", "bangalore", "chennai", "kolkata", "pune", "hyderabad",
                    "ahmedabad", "jaipur", "surat", "lucknow", "kanpur", "nagpur", "indore",
                    "kochi", "thiruvananthapuram", "coimbatore", "madurai", "salem", "tiruchirappalli"
                ]
                address_lower = address.lower()
                for city in indian_cities:
                    if city in address_lower:
                        parsed_data["city"] = city.title()
                        break

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
            enriched_data["gender"] = get_final_gender(parsed_data.get("full_name", ""), trimmed_text)

        # Step 6.2: Add pincode if city is present
        city = enriched_data.get("city")
        if city and not enriched_data.get("pincode") and not enriched_data.get("pin_code"):
            pincode = get_pincode_by_city(city)
            if pincode:
                enriched_data["pincode"] = pincode
                enriched_data["pin_code"] = pincode

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