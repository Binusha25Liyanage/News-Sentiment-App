"""News fetcher for Editorial Intelligence Dashboard."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
LAST_NEWS_ERROR = ""


def get_news_error():
    """Return the most recent NewsAPI error message."""
    return LAST_NEWS_ERROR


def get_news(topic, count=10):
    """Fetch latest news for a topic from NewsAPI.

    Args:
        topic: Search keyword or phrase.
        count: Maximum number of articles to return.

    Returns:
        A list of dictionaries with keys: title, description, url, publishedAt, source.
        Returns an empty list if configuration or API calls fail.
    """
    global LAST_NEWS_ERROR
    LAST_NEWS_ERROR = ""

    api_key = os.getenv("NEWS_API_KEY")
    if not api_key or api_key == "your_key_here":
        LAST_NEWS_ERROR = "NEWS_API_KEY is missing or still set to 'your_key_here'."
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
        payload = response.json()

        if response.status_code != 200:
            LAST_NEWS_ERROR = payload.get("message") or f"NewsAPI request failed with HTTP {response.status_code}."
            return []

        if payload.get("status") != "ok":
            LAST_NEWS_ERROR = payload.get("message") or "NewsAPI returned a non-ok status."
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
    except requests.Timeout:
        LAST_NEWS_ERROR = "NewsAPI request timed out."
        return []
    except requests.ConnectionError:
        LAST_NEWS_ERROR = "Could not connect to NewsAPI. Check internet connectivity."
        return []
    except (requests.RequestException, ValueError, TypeError) as exc:
        LAST_NEWS_ERROR = f"Unexpected NewsAPI error: {exc}"
        return []
