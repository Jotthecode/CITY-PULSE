import requests

def get_osm_places(query, lat, lon):
    """Search for places near given coordinates using OSM Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "viewbox": f"{lon-0.05},{lat+0.05},{lon+0.05},{lat-0.05}",  # bounding box
        "bounded": 1
    }
    headers = {"User-Agent": "CITY-PULSE-App"}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

