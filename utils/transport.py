import requests
import os

# Get your data.gov.in API key
DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")

# IMPORTANT: YOU MUST POPULATE THIS DICTIONARY WITH ACTUAL RESOURCE IDs
# from data.gov.in for the cities you want to cover.
# Example format:
INDIA_TRANSPORT_RESOURCES = {
    "Mumbai": {
        # Search on data.gov.in for "Mumbai Bus Routes" or similar
        # Find the resource ID for the specific dataset you want
        "bus_routes_id": "YOUR_MUMBAI_BUS_ROUTES_RESOURCE_ID", # Example: 'a12b3c4d-e5f6-7890-1234-567890abcdef'
        "local_train_stations_id": "YOUR_MUMBAI_LOCAL_TRAIN_STATIONS_RESOURCE_ID", # Example: 'b23c4d5e-f6a7-8901-2345-67890abcdef1'
    },
    "Delhi": {
        # Search on data.gov.in for "Delhi Metro Stations"
        "metro_stations_id": "YOUR_DELHI_METRO_STATIONS_RESOURCE_ID",
        # Search for "Delhi Bus Routes"
        "bus_routes_id": "YOUR_DELHI_BUS_ROUTES_RESOURCE_ID",
    },
    "Bengaluru": {
        "metro_stations_id": "YOUR_BENGALURU_METRO_STATIONS_RESOURCE_ID",
        "bus_routes_id": "YOUR_BENGALURU_BMTC_ROUTES_RESOURCE_ID",
    },
    "Chennai": {
        "mrt_stations_id": "YOUR_CHENNAI_MRTS_RESOURCE_ID",
    },
    "Kolkata": {
        "metro_stations_id": "YOUR_KOLKATA_METRO_STATIONS_RESOURCE_ID",
    },
    "Pune": {
        "bus_routes_id": "YOUR_PUNE_PMPML_ROUTES_RESOURCE_ID",
    },
    "Hyderabad": {
        "metro_stations_id": "YOUR_HYDERABAD_METRO_STATIONS_RESOURCE_ID",
    },
    "Ahmedabad": {
        "brts_routes_id": "YOUR_AHMEDABAD_BRTS_ROUTES_RESOURCE_ID",
    },
    # Add more Tier 1 and Tier 2 cities as you research their resource IDs
}


def fetch_data_from_gov_in(resource_id):
    """
    Fetches data from the data.gov.in API for a given resource ID.
    """
    if not DATA_GOV_IN_API_KEY:
        return {"error": "DATA_GOV_IN_API_KEY is not set in environment variables."}

    base_url = f"https://api.data.gov.in/resource/{resource_id}"
    params = {
        "api-key": DATA_GOV_IN_API_KEY,
        "format": "json",
        "limit": 500 # Adjust limit as needed. Max is often 1000 per request.
                     # For very large datasets, you might need to implement pagination.
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get("records", []) # data.gov.in usually returns data in a "records" list
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data from data.gov.in (Resource ID: {resource_id}): {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while processing data.gov.in response: {e}"}


def get_public_transport_info(city):
    """
    Gathers static public transport information for a given Indian city
    from data.gov.in.
    """
    transport_info = {
        "status": "No static transport data available for this city from data.gov.in.",
        "stations": [],  # List of dictionaries for stations/stops
        "lines": [],     # List of dictionaries for routes/lines
        "error": None
    }

    city_resources = INDIA_TRANSPORT_RESOURCES.get(city)

    if not city_resources:
        return transport_info # No resources configured for this city

    # --- Process Bus Routes ---
    if "bus_routes_id" in city_resources:
        bus_routes_data = fetch_data_from_gov_in(city_resources["bus_routes_id"])
        if "error" in bus_routes_data:
            transport_info["error"] = bus_routes_data["error"]
        else:
            for record in bus_routes_data:
                # IMPORTANT: Adjust 'route_number', 'start_point', 'end_point'
                # to the actual column names in the data.gov.in dataset.
                route_num = record.get("route_number", record.get("route_id", "N/A"))
                start = record.get("start_point", "N/A")
                end = record.get("end_point", "N/A")
                if route_num != "N/A":
                    transport_info["lines"].append({
                        "Type": "Bus",
                        "Route Number": route_num,
                        "Start": start,
                        "End": end
                    })
            if bus_routes_data:
                transport_info["status"] = "Static bus route data available."

    # --- Process Metro/Local Train Stations ---
    # This block can be extended for metro_stations_id, local_train_stations_id, etc.
    # based on what you find on data.gov.in.
    # Make sure to handle unique column names for each dataset.

    if "metro_stations_id" in city_resources:
        metro_stations_data = fetch_data_from_gov_in(city_resources["metro_stations_id"])
        if "error" in metro_stations_data:
            transport_info["error"] = metro_stations_data["error"]
        else:
            for record in metro_stations_data:
                # IMPORTANT: Adjust 'station_name', 'latitude', 'longitude'
                # to the actual column names in the data.gov.in dataset.
                name = record.get("station_name", record.get("stop_name", "N/A"))
                lat_str = record.get("latitude", record.get("lat"))
                lon_str = record.get("longitude", record.get("lon"))

                try:
                    lat = float(lat_str) if lat_str else None
                    lon = float(lon_str) if lon_str else None
                except (ValueError, TypeError):
                    lat, lon = None, None # Handle non-numeric or missing coords

                if name != "N/A":
                    transport_info["stations"].append({
                        "Name": name,
                        "Type": "Metro Station",
                        "Latitude": lat,
                        "Longitude": lon
                    })
            if metro_stations_data:
                if "bus" in transport_info["status"]:
                    transport_info["status"] += " & static metro station data available."
                else:
                    transport_info["status"] = "Static metro station data available."

    # General message about real-time (since it's not the focus here)
    transport_info["realtime_updates"] = [{"message": "Real-time updates are not available via this API for Indian cities."}]

    return transport_info