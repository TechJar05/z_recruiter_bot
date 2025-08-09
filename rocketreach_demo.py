# import requests

# # Replace with your actual RocketReach API key
# API_KEY = "1a792d2k772ef478ff44d61a9709fa271387f5e8"

# # Example lookup by LinkedIn URL (you can also use email)
# linkedin_url = "https://www.linkedin.com/in/yash-rajbhoj/"

# # Construct the API URL
# url = "https://api.rocketreach.co/v1/api/lookupProfile"

# # Set headers and payload
# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# payload = {
#     "linkedin_url": linkedin_url
# }

# # Make the POST request
# response = requests.post(url, headers=headers, json=payload)

# # Handle the response
# if response.status_code == 200:
#     data = response.json()
#     print("✅ User Found:")
#     print("Name:", data.get("name"))
#     print("Email:", data.get("email"))
#     print("Current Job Title:", data.get("current_title"))
#     print("Company:", data.get("current_employer"))
#     print("Location:", data.get("location"))
#     print("Education:", data.get("education"))
#     print("\nFull JSON Response:")
#     print(data)
# else:
#     print("❌ Failed to retrieve data.")
#     print("Status Code:", response.status_code)
#     print("Response:", response.text)






# import requests

# ROCKETREACH_API_KEY = '1a792d2k599bbc7a3fbb1acbe27adc33af02fffc'  # Replace with your real API key
# url = "https://api.rocketreach.co/v1/api/lookupProfile"

# headers = {
#     "Authorization": f"Bearer {ROCKETREACH_API_KEY}",
#     "Content-Type": "application/json"
# }

# params = {
#     "linkedin_url": "https://www.linkedin.com/in/yash-rajbhoj/"  # Replace with real LinkedIn URL
# }

# response = requests.get(url, headers=headers, params=params)

# if response.status_code == 200:
#     print("✅ Success! User info:")
#     print(response.json())
# else:
#     print("❌ Failed to retrieve data.")
#     print("Status Code:", response.status_code)
#     print("Response:", response.text)



import requests

API_KEY = "1a792d2k599bbc7a3fbb1acbe27adc33af02fffc"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

params = {
    "linkedin_url": "https://www.linkedin.com/in/shrutibelgamwar"
}

url = "https://api.rocketreach.co/v1/lookupProfile" 


response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    print("✅ Success: User Data Found")
    print(data)
else:
    print("❌ Failed to retrieve data.")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
