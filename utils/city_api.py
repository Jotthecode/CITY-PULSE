# utils/city_api.py
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def search_cities(query):
    """Returns a list of city dicts matching the query"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={api_key}"
    res = requests.get(url)
    if res.status_code == 200:
        cities = res.json()
        # Return cleaned-up city display + coordinates
        return [{
            "label": f"{c['name']}, {c.get('state', '')}, {c['country']}",
            "lat": c["lat"],
            "lon": c["lon"]
        } for c in cities]
    return []
