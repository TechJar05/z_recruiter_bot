import requests

def get_pincode_by_city(city_name):
    city_name = city_name.strip().title()
    url = f"https://world-pincode-api.p.rapidapi.com/api/pincode-from-city?city={city_name}"

    headers = {
        "X-RapidAPI-Key": "c48100439amsh59c391945abd1ccp14ce9djsn20ae0df59079",
        "X-RapidAPI-Host": "world-pincode-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    # print(f"Fetching pincode for city: {city_name}")
    # print("API Response:", response.status_code, response.text)

    if response.status_code == 200:
        data = response.json()
        if data and "data" in data and isinstance(data["data"], list):
            return data["data"][0].get("pincode") or data["data"][0].get("pin_code")
    return None

# Example usage
# pincode = get_pincode_by_city("Mumbai")
# print("Pincode:", pincode)
