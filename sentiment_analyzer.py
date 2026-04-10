"""
Sentiment Analyzer Module
Analyzes sentiment of news headlines using Google Gemini API.
"""

import os
import json
import re
from dotenv import load_dotenv

# Import Google Generative AI library
try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed. Install it with: pip install google-generativeai")
    genai = None

# Load environment variables from .env file
load_dotenv()

def analyze_sentiment(headline):
    """
    Analyze the sentiment of a news headline using Google Gemini API.
    
    Args:
        headline (str): The news headline to analyze
    
    Returns:
        dict: A dictionary containing:
            - sentiment (str): "positive", "neutral", or "negative"
            - score (float): Sentiment score from -1.0 to 1.0
                            (-1.0 = very negative, 0.0 = neutral, 1.0 = very positive)
            - reason (str): A short one-sentence explanation of the sentiment
        
        Returns a dict with error information if analysis fails.
    
    Raises:
        None: Errors are caught and logged gracefully.
    """
    
    # Check if genai library is available
    if genai is None:
        return {
            "sentiment": "error",
            "score": 0.0,
            "reason": "google-generativeai library not installed"
        }
    
    # Load the GEMINI_API_KEY from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Check if API key is set
    if not api_key or api_key == "your_key_here":
        return {
            "sentiment": "error",
            "score": 0.0,
            "reason": "GEMINI_API_KEY not set in .env file"
        }
    
    try:
        # Configure the Gemini API with the API key
        genai.configure(api_key=api_key)
        
        # Create a model instance (using gemini-pro for text analysis)
        model = genai.GenerativeModel("gemini-pro")
        
        # Craft a detailed prompt for sentiment analysis
        prompt = f"""Analyze the sentiment of the following news headline and respond with ONLY a valid JSON object (no additional text before or after).

Headline: "{headline}"

Respond with exactly this JSON format:
{{"sentiment": "positive|neutral|negative", "score": <number from -1.0 to 1.0>, "reason": "<short one-sentence explanation>"}}

Important:
- sentiment must be: "positive", "neutral", or "negative"
- score must be a float between -1.0 and 1.0 (e.g., 0.75, -0.3, 0.0)
- reason must be a concise one-sentence explanation
- Return ONLY the JSON object, nothing else"""
        
        # Call the Gemini API
        response = model.generate_content(prompt)
        
        # Extract the response text
        response_text = response.text.strip()
        
        # Try to extract JSON from the response (in case of extra text)
        # Look for JSON object pattern
        json_match = re.search(r'\{[^{}]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)
        
        # Parse the JSON response
        result = json.loads(response_text)
        
        # Validate the response structure
        if not all(key in result for key in ["sentiment", "score", "reason"]):
            return {
                "sentiment": "error",
                "score": 0.0,
                "reason": "Invalid response format from Gemini API"
            }
        
        # Ensure sentiment is valid
        if result["sentiment"] not in ["positive", "neutral", "negative"]:
            result["sentiment"] = "neutral"
        
        # Ensure score is within bounds
        score = float(result["score"])
        result["score"] = max(-1.0, min(1.0, score))
        
        # Truncate reason if too long
        result["reason"] = str(result["reason"])[:100]
        
        return result
    
    except json.JSONDecodeError:
        return {
            "sentiment": "error",
            "score": 0.0,
            "reason": "Failed to parse Gemini API response as JSON"
        }
    
    except AttributeError:
        return {
            "sentiment": "error",
            "score": 0.0,
            "reason": "Gemini API did not return a valid response"
        }
    
    except Exception as e:
        return {
            "sentiment": "error",
            "score": 0.0,
            "reason": f"Error analyzing sentiment: {str(e)[:50]}"
        }
