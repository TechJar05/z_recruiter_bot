

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
