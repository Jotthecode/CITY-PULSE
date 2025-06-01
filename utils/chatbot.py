# utils/chatbot.py

import requests

# Replace these with env variables or config if you want
GOOGLE_API_KEY = "AIzaSyAIQcBW-1Wmx4Z8vuvyibvrum9dS0HgheI"
CSE_ID = "41a7d2bcb1d014824"

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
