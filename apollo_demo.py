

import requests
import json

# 🔐 Apollo API Key (keep this secure)
API_KEY = 'VZ_OvcM-Q2BUsi7xM7vzcg'  # Replace with your real API key

# 🔗 Target LinkedIn profile URL
linkedin_url = 'https://linkedin.com/in/omkar-latambale/'

# 🔍 Match endpoint (GET request with query param)
url = 'https://api.apollo.io/v1/people/match'
params = {
    'linkedin_url': linkedin_url
}

# 🛡 Headers
headers = {
    'X-Api-Key': API_KEY,
    'Content-Type': 'application/json'
}

# 📡 Make the request
response = requests.get(url, headers=headers, params=params)

# 🔄 Handle the response
if response.status_code == 200:
    person = response.json().get('person', {})

    if not person:
        print("❌ No person found.")
    else:
        print("\n✅ Person Found:\n")

        # 📄 Basic Info
        print(f"👤 Name       : {person.get('name')}")
        print(f"📧 Email      : {person.get('email')}")
        print(f"💼 Title      : {person.get('title')}")
        print(f"🏢 Company    : {person.get('organization', {}).get('name')}")
        print(f"📍 Location   : {person.get('city')}, {person.get('state')}, {person.get('country')}")
        print(f"🔗 LinkedIn   : {person.get('linkedin_url')}")
        print(f"🖼 Photo      : {person.get('photo_url')}")
        print(f"🧠 Headline   : {person.get('headline')}")
        print()

        # 📚 Employment History
        print("📌 Employment History:")
        for job in person.get('employment_history', []):
            org = job.get('organization_name', 'N/A')
            title = job.get('title', 'N/A')
            start = job.get('start_date', 'N/A')
            end = job.get('end_date', 'Present' if job.get('current') else job.get('end_date'))
            print(f" - {title} at {org} ({start} to {end})")
        print()

        # 🏢 Organization Details
        organization = person.get('organization', {})
        if organization:
            print("🏢 Organization Info:")
            print(f" - Name         : {organization.get('name')}")
            print(f" - Website      : {organization.get('website_url')}")
            print(f" - Industry     : {', '.join(organization.get('industries', []))}")
            print(f" - Location     : {organization.get('raw_address')}")
            print(f" - Phone        : {organization.get('phone')}")
            print(f" - LinkedIn     : {organization.get('linkedin_url')}")
            print(f" - Description  : {organization.get('short_description')}")
else:
    print(f"\n❌ Request failed: {response.status_code}")
    try:
        print("🔍 Error:", response.json().get("error", "No error message"))
    except:
        print("🔍 Response:", response.text)
































# # with word document

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









# apollo api



# # # # # linkedin parsing
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# import os
# from django.conf import settings

# APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'


# class ApolloLinkedInLookupAPIView(APIView):
#     def post(self, request):
#         linkedin_url = request.data.get("linkedin_url")

#         if not linkedin_url:
#             return Response({"error": "linkedin_url is required"}, status=status.HTTP_400_BAD_REQUEST)

#         headers = {"X-Api-Key":settings.APOLLO_API_KEY}
#         params = {"linkedin_url": linkedin_url}

#         try:
#             apollo_response = requests.get(APOLLO_BASE_URL, headers=headers, params=params)

#             try:
#                 data = apollo_response.json()
#             except ValueError:
#                 return Response({
#                     "error": "Apollo API did not return valid JSON.",
#                     "status_code": apollo_response.status_code,
#                     "raw_response": apollo_response.text  # helpful for debugging
#                 }, status=apollo_response.status_code)

#             return Response(data, status=apollo_response.status_code)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

