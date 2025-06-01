import requests
import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Or hardcode for testing

def get_air_quality(city):
    # Step 1: Get coordinates of the city
    geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        "q": city,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }
    geo_res = requests.get(geocoding_url, params=geo_params)
    geo_data = geo_res.json()

    if not geo_data:
        return {"error": "City not found"}

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # Step 2: Get air pollution data
    air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY
    }
    air_res = requests.get(air_url, params=air_params)
    air_data = air_res.json()

    if "list" not in air_data:
        return {"error": "No air quality data available"}

    air_info = air_data["list"][0]
    aqi = air_info["main"]["aqi"]  # AQI from 1 to 5

    return {
        "aqi": aqi,
        "components": air_info["components"]
    }
