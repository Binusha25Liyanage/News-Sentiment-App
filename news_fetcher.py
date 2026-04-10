"""
News Fetcher Module
Fetches live news headlines from NewsAPI based on a given topic.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_news(topic, count=10):
    """
    Fetch news headlines from NewsAPI for a given topic.
    
    Args:
        topic (str): The topic to search for (e.g., "Tesla", "Sri Lanka economy", "AI")
        count (int): Number of articles to fetch (default: 10)
    
    Returns:
        list: A list of dictionaries containing:
            - title (str): Article headline
            - description (str): Brief description of the article
            - url (str): Link to the full article
            - publishedAt (str): Publication date and time
            - source (str): News source name
        
        Returns empty list if API call fails with a descriptive error message.
    
    Raises:
        None: Errors are caught and logged gracefully.
    """
    
    # Load the NEWS_API_KEY from environment variables
    api_key = os.getenv("NEWS_API_KEY")
    
    # Check if API key is set
    if not api_key or api_key == "your_key_here":
        print("ERROR: NEWS_API_KEY not set in .env file. Please add your NewsAPI key.")
        return []
    
    # NewsAPI endpoint URL
    url = "https://newsapi.org/v2/everything"
    
    # Parameters for the API request
    params = {
        "q": topic,  # Search query
        "sortBy": "publishedAt",  # Sort by most recent
        "pageSize": count,  # Number of articles to fetch
        "apiKey": api_key,
        "language": "en"  # English articles only
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Check if the API call was successful
        if data.get("status") != "ok":
            print(f"ERROR: NewsAPI returned status '{data.get('status')}': {data.get('message')}")
            return []
        
        # Extract articles and format them
        articles = data.get("articles", [])
        formatted_articles = []
        
        for article in articles:
            formatted_articles.append({
                "title": article.get("title", "N/A"),
                "description": article.get("description", "N/A"),
                "url": article.get("url", "#"),
                "publishedAt": article.get("publishedAt", "N/A"),
                "source": article.get("source", {}).get("name", "Unknown")
            })
        
        return formatted_articles
    
    except requests.exceptions.Timeout:
        print("ERROR: Request to NewsAPI timed out. Please try again.")
        return []
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Failed to connect to NewsAPI. Check your internet connection.")
        return []
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("ERROR: Invalid NEWS_API_KEY. Please check your .env file.")
        elif response.status_code == 429:
            print("ERROR: Rate limit exceeded. Please try again later.")
        else:
            print(f"ERROR: HTTP Error {response.status_code}: {e}")
        return []
    
    except ValueError:
        print("ERROR: Failed to parse NewsAPI response. The API might be unavailable.")
        return []
    
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while fetching news: {str(e)}")
        return []
