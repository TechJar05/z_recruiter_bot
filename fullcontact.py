import requests

FULLCONTACT_API_KEY = "your_fullcontact_api_key"  # Replace with your API key
email = "dhotrednyanu@gmail.com"  # You must have this from another API

url = "https://api.fullcontact.com/v3/person.enrich"

headers = {
    "Authorization": f"Bearer {FULLCONTACT_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "email": email
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print("✅ Enriched Data:")
    for key, value in data.items():
        print(f"{key}: {value}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")
