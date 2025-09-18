# utils/chatbot.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Load API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("CSE_ID")

# Validate that required environment variables are set
if not GOOGLE_API_KEY:
    raise ValueError("Missing required environment variable: GOOGLE_API_KEY")
if not CSE_ID:
    raise ValueError("Missing required environment variable: CSE_ID")

def search_google(query):
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_API_KEY,
                "cx": CSE_ID,
                "q": query
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                results = data["items"][:3]  # Limit to top 3 results
                output = "\n\n".join(
                    [f"**[{item['title']}]({item['link']})**\n{item['snippet']}" for item in results]
                )
                return output
            else:
                return "No relevant results found."
        else:
            return f"Google API Error: {response.status_code}"

    except Exception as e:
        return f"Exception during search: {str(e)}"
