# import requests
# import time

# # Replace with your own details
# API_KEY = 'UlwyzmKovZUjlObXZc74P0IsOyfF7Mf8HxXR6bEOXX8'
# PHANTOM_ID = '8229846154297747'  # e.g. '8229846154297747'

# # Step 1: Launch the Phantom
# launch_url = f'https://api.phantombuster.com/api/v2/agents/launch'
# headers = {
#     'X-Phantombuster-Key-1': API_KEY,
#     'Content-Type': 'application/json'
# }
# payload = {
#     'id': PHANTOM_ID,
#     'output': 'first-result-object'  # So we get the latest result
# }

# print("Launching Phantom...")
# response = requests.post(launch_url, headers=headers, json=payload)
# launch_data = response.json()

# if not launch_data.get("data") or not launch_data["data"].get("containerId"):
#     print("Failed to launch Phantom. Check your Phantom ID and API key.")
#     print(launch_data)
#     exit()

# # Step 2: Wait for it to finish
# container_id = launch_data["data"]["containerId"]
# print(f"Phantom launched. Waiting for container {container_id} to complete...")

# status_url = f'https://api.phantombuster.com/api/v2/containers/fetch?id={container_id}'
# while True:
#     status_response = requests.get(status_url, headers=headers)
#     status_data = status_response.json()
#     if status_data["data"]["status"] == "success":
#         print("Phantom completed successfully!")
#         break
#     elif status_data["data"]["status"] == "failed":
#         print("Phantom failed to run.")
#         exit()
#     else:
#         print("Waiting...")
#         time.sleep(10)

# # Step 3: Get output file
# result_url = status_data["data"]["resultObjectUrl"]
# print(f"\n🔗 Result file URL: {result_url}")

# # Optional: download the CSV file
# csv_response = requests.get(result_url)
# with open("linkedin_data.csv", "wb") as f:
#     f.write(csv_response.content)
#     print("✅ LinkedIn data saved as 'linkedin_data.csv'")





import time
import requests

PHANTOM_API_KEY = 'UlwyzmKovZUjlObXZc74P0IsOyfF7Mf8HxXR6bEOXX8'
PHANTOM_ID = '8229846154297747'

headers = {
    'X-Phantombuster-Key-1': PHANTOM_API_KEY,
    'Content-Type': 'application/json'
}

def is_phantom_ready():
    status_response = requests.get(
        f"https://api.phantombuster.com/api/v2/agents/fetch?id={PHANTOM_ID}",
        headers={"X-Phantombuster-Key-1": PHANTOM_API_KEY}
    )
    data = status_response.json()
    print("DEBUG response:", data)  # Debug output

    # Check if the agent is not currently running
    agent = data.get("agent", {})
    is_running = agent.get("currentLaunch") is not None

    if not is_running:
        return True
    else:
        print("Phantom is still running.")
        return False




# Step 2: Wait if it's not ready
print("Checking if Phantom is available...")
while not is_phantom_ready():
    print("Phantom is busy. Waiting 10 seconds...")
    time.sleep(10)

# Step 3: Launch Phantom
url = 'https://api.phantombuster.com/api/v2/agents/launch'
payload = {
    "id": PHANTOM_ID,
    "argument": {
        "search": "https://www.linkedin.com/search/results/people/?currentCompany=%5B%221353%22%5D&geoUrn=%5B%22102713980%22%5D&industry=%5B%221810%22%5D&keywords=Pune&origin=FACETED_SEARCH&pastCompany=%5B%22157240%22%5D&profileLanguage=%5B%22en%22%5D&schoolFilter=%5B%2215094398%22%5D",
        "numberOfProfiles": 20
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())




import time
import requests

def get_result_url(container_id):
    time.sleep(10)  # Optional: wait to let Phantom complete
    result_url = f"https://api.phantombuster.com/api/v2/containers/fetch-output?id={container_id}"
    response = requests.get(result_url, headers=headers)
    return response.json()

# Example usage
container_id = response.json().get("containerId")
if container_id:
    result = get_result_url(container_id)
    print("Download URL:", result.get("url"))
else:
    print("No containerId found.")
