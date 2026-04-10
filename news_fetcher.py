"""News fetcher for Editorial Intelligence Dashboard."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_news(topic, count=10):
    """Fetch latest news for a topic from NewsAPI.

    Args:
        topic: Search keyword or phrase.
        count: Maximum number of articles to return.

    Returns:
        A list of dictionaries with keys: title, description, url, publishedAt, source.
        Returns an empty list if configuration or API calls fail.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key or api_key == "your_key_here":
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "sortBy": "publishedAt",
        "pageSize": count,
        "language": "en",
        "apiKey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") != "ok":
            return []

        articles = payload.get("articles", [])
        return [
            {
                "title": article.get("title") or "Untitled",
                "description": article.get("description") or "",
                "url": article.get("url") or "#",
                "publishedAt": article.get("publishedAt") or "",
                "source": (article.get("source") or {}).get("name", "Unknown"),
            }
            for article in articles
        ]
    except (requests.RequestException, ValueError, TypeError):
        return []
