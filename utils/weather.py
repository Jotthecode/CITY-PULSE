import os
import requests
from dotenv import load_dotenv
load_dotenv()
# This script fetches the current weather for a specified city using OpenWeatherMap API
OWM_API = os.getenv("OPENWEATHER_API_KEY")
VC_API = os.getenv("VISUALCROSSING_API_KEY")

def get_current_weather(city_name, lat, lon):
    """Fetch current weather using OpenWeatherMap."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OWM_API}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch current weather"}

    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"]
    }

def get_monthly_weather(city_name):
    """Fetch monthly weather summary from Visual Crossing."""
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{city_name}?unitGroup=metric&include=months&key={VC_API}&contentType=json"
    )
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch monthly weather"}

    data = response.json()
    months = data.get("months", [])
    output = []

    for month in months:
        output.append({
            "month": month["month"],
            "avg_temp": month["temp"],
            "humidity": month["humidity"],
            "precip": month["precip"]
        })

    return output
