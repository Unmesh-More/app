import requests
from config import API_KEY, BASE_URL

def get_weather(lat, lon):

    params = {
        "key": API_KEY,
        "q": f"{lat},{lon}",
        "aqi": "no"
    }

    try:
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            weather = {
                "city": data["location"]["name"],
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "wind_speed": data["current"]["wind_kph"],
                "description": data["current"]["condition"]["text"]
            }

            return weather

        else:
            print("Weather API Error:", response.status_code)
            print(response.text)
            return None

    except Exception as e:
        print("Request Failed:", e)
        return None