import requests
import os

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Set your NewsAPI key in env variables

def get_crime_news(city):
    url = "https://newsapi.org/v2/everything"
    query = f"crime AND {city}"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        news = []
        for article in articles:
            news.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "publishedAt": article.get("publishedAt")
            })
        return news
    except Exception as e:
        return [{"error": str(e)}]
