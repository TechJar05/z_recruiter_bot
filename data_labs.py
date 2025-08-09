import requests

# Replace this with your actual API key
PDL_API_KEY = "08715d17187d5a43e4a29fafef63f002302efbf72ed223224b8f10dde4ddfc6c"

# Replace with the LinkedIn URL you want to look up
linkedin_url = "https://www.linkedin.com/in/shrutibelgamwar"

url = "https://api.peopledatalabs.com/v5/person/enrich"

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": PDL_API_KEY
}

payload = {
    "profile": linkedin_url
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("✅ Profile Found:")
    print(response.json())
else:
    print(f"❌ Error {response.status_code}: {response.text}")
