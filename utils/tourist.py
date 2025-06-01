from pytrends.request import TrendReq
import requests
import os

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")  # or hardcode it like: 'YOUR_API_KEY'

# Define a custom User-Agent to help avoid 429 errors
CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"

def get_recommendations(city):
    # Use custom headers with pytrends
    pytrends = TrendReq(
        hl='en-US',
        tz=360,
        requests_args={
            "headers": {
                "User-Agent": CUSTOM_USER_AGENT
            }
        }
    )

    keyword = f"tourist places in {city}"

    trends = []
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo='', gprop='')
        interest = pytrends.interest_over_time()

        if not interest.empty:
            for ts, row in interest.iterrows():
                trends.append({
                    "date": str(ts.date()),
                    "interest": int(row[keyword])
                })
    except Exception as e:
        trends = [{"error": f"Google Trends fetch failed: {str(e)}"}]

    # Google Places API (optional)
    places = []
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"top tourist attractions in {city}",
            "key": GOOGLE_PLACES_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()

        for place in data.get("results", [])[:10]:
            places.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating")
            })
    except Exception as e:
        places = [{"error": f"Google Places API failed: {str(e)}"}]

    return {
        "trends": trends,
        "places": places
    }
