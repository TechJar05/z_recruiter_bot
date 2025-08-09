

import requests
import json

# 🔐 Apollo API Key (keep this secure)
API_KEY = 'VZ_OvcM-Q2BUsi7xM7vzcg'  # Replace with your real API key

# 🔗 Target LinkedIn profile URL
linkedin_url = 'https://www.linkedin.com/in/yash-rajbhoj/'

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






# data wwith education details

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# from django.conf import settings

# APOLLO_BASE_URL = 'https://api.apollo.io/api/v1/people/match'
# SERP_API_URL = "https://serpapi.com/search.json"
# SERP_API_KEY='340f098c1ebb9d4fa93623326b3c408baec55aba5bc7ff7da7fce288e1b21a90'

# class LinkedInDataCombinedAPIView(APIView):
#     def post(self, request):
#         linkedin_url = request.data.get("linkedin_url")

#         if not linkedin_url:
#             return Response({"error": "linkedin_url is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Step 1: Fetch data from Apollo
#             apollo_headers = {"X-Api-Key": settings.APOLLO_API_KEY}
#             apollo_params = {"linkedin_url": linkedin_url}
#             apollo_response = requests.get(APOLLO_BASE_URL, headers=apollo_headers, params=apollo_params)

#             if apollo_response.status_code != 200:
#                 return Response({
#                     "error": "Apollo API failed",
#                     "details": apollo_response.text
#                 }, status=apollo_response.status_code)

#             apollo_data = apollo_response.json()

#             # Step 2: Fetch education from SerpApi
#             serp_params = {
#                 "engine": "linkedin_profile",
#                 "url": linkedin_url,
#                 "api_key": SERP_API_KEY
#             }

#             serp_response = requests.get(SERP_API_URL, params=serp_params)

#             if serp_response.status_code != 200:
#                 education_data = []
#                 serp_error = serp_response.text
#             else:
#                 serp_json = serp_response.json()
#                 education_data = serp_json.get("education", [])

#             # Step 3: Combine and return
#             return Response({
#                 "apollo_data": apollo_data,
#                 "education_data": education_data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": "Unexpected error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#  rocket reach api testing

# # views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# import os

# ROCKETREACH_API_KEY = os.getenv("1a792d2k772ef478ff44d61a9709fa271387f5e8")
# ROCKETREACH_URL = "https://api.rocketreach.co/v1/api/lookupProfile"

# class RocketReachLookupAPIView(APIView):
#     def post(self, request):
#         linkedin_url = request.data.get("linkedin_url")
#         if not linkedin_url:
#             return Response({"error": "LinkedIn URL is required"}, status=400)

#         headers = {
#             "Authorization": f"Bearer {ROCKETREACH_API_KEY}"
#         }

#         params = {
#             "linkedin_url": linkedin_url
#         }

#         try:
#             response = requests.get(ROCKETREACH_URL, headers=headers, params=params)
#             data = response.json()

#             if response.status_code == 200:
#                 return Response(data, status=200)
#             else:
#                 return Response(data, status=response.status_code)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
