# 📰 News Sentiment Tracker

A real-time web application that fetches news headlines and analyzes their sentiment using Google Gemini AI. Built with Python, Streamlit, and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Overview

**News Sentiment Tracker** helps you understand the emotional tone and sentiment of news articles on any topic. Simply enter a topic, and the app will:

1. 📡 Fetch 10 latest headlines using **NewsAPI**
2. 🤖 Analyze sentiment using **Google Gemini AI**
3. 📊 Visualize results with interactive charts
4. 📑 Display detailed analysis with scores and explanations

Perfect for:
- Market researchers tracking news sentiment about companies or industries
- Investors monitoring news sentiment for investment decisions
- Journalists analyzing narrative trends
- Students learning NLP and sentiment analysis concepts

## ✨ Features

- **Real-time News Fetching**: Get the latest headlines from NewsAPI with advanced filtering
- **AI Sentiment Analysis**: Powered by Google Gemini for accurate, contextual sentiment analysis
- **Interactive Dashboard**: Beautiful Streamlit UI with dark sidebar
- **Live Visualizations**:
  - 🥧 Pie chart showing sentiment distribution (positive/neutral/negative)
  - 📊 Bar chart displaying sentiment scores per headline
- **Detailed Analytics**:
  - Summary metrics: Total articles, positive/neutral/negative counts
  - Interactive data table with sources, headlines, sentiment, scores, and AI reasoning
- **Export Results**: Download analysis results as CSV for further processing
- **Error Handling**: Graceful error management with helpful error messages
- **Environment-based Configuration**: Secure API key management using `.env`

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend/Frontend** | Python 3.8+ |
| **Web Framework** | Streamlit |
| **sentiment Analysis** | Google Gemini API |
| **News Source** | NewsAPI |
| **Data Processing** | Pandas |
| **Visualization** | Plotly |
| **Environment Management** | python-dotenv |
| **HTTP Requests** | requests |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Active internet connection

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/news-sentiment-tracker.git
cd news-sentiment-tracker
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install streamlit pandas plotly requests python-dotenv google-generativeai
```

## 🔑 Configuration

### 1. Get API Keys

#### NewsAPI Key
1. Visit [https://newsapi.org](https://newsapi.org)
2. Sign up for a free account
3. Copy your API key from the dashboard

#### Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the generated key

### 2. Create `.env` File

Create a `.env` file in the project root directory:

```bash
# Windows PowerShell
New-Item .env

# macOS/Linux
touch .env
```

### 3. Add API Keys to `.env`

Open `.env` and add:

```
GEMINI_API_KEY=your_gemini_api_key_here
NEWS_API_KEY=your_newsapi_key_here
```

**⚠️ Important:** Never commit the `.env` file to version control! It's already in `.gitignore`.

## 🚀 Quick Start

### Run the Application

```bash
streamlit run app.py
```

The app will start at `http://localhost:8501`

### How to Use

1. **Enter a Topic**: Type any news topic (e.g., "Tesla", "Climate change", "Cryptocurrency")
2. **Click "Analyze News"**: The app will fetch 10 headlines and analyze each one
3. **View Results**:
   - See summary metrics
   - Check sentiment distribution pie chart
   - Explore sentiment scores bar chart
   - Read detailed analyses in the table
4. **Export Results**: Download the analysis as CSV for external use

## 📁 Project Structure

```
news-sentiment-tracker/
├── .env                       # API keys (add your keys here)
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── app.py                     # Main Streamlit application
├── news_fetcher.py            # NewsAPI integration
└── sentiment_analyzer.py      # Google Gemini sentiment analysis
```

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit dashboard with UI, visualizations, and table display |
| `news_fetcher.py` | Fetches news articles from NewsAPI based on topic search |
| `sentiment_analyzer.py` | Sends headlines to Google Gemini for sentiment analysis |
| `.env` | Stores API keys (never commit this file) |
| `requirements.txt` | List of Python package dependencies |

## 🧠 How It Works

### Workflow

```
User Input (Topic)
       ↓
   news_fetcher.py
   (NewsAPI call)
       ↓
   10 Headlines
       ↓
   sentiment_analyzer.py
   (For each headline)
       ↓
   Google Gemini API
       ↓
   Sentiment JSON
   {sentiment, score, reason}
       ↓
   app.py (Process & Display)
       ↓
   Visualizations & Table
```

### Sentiment Analysis Details

**Input**: News headline text

**Output**: JSON object with:
- **sentiment** (string): "positive", "neutral", or "negative"
- **score** (float): -1.0 to 1.0 (negative to positive)
- **reason** (string): AI-generated one-sentence explanation

**Example**:
```json
{
  "sentiment": "negative",
  "score": -0.75,
  "reason": "The headline expresses concern about declining market performance."
}
```

## 📊 Visualization Examples

### Sentiment Distribution Pie Chart
- Shows percentage breakdown of positive, neutral, and negative articles
- Color-coded: 🟢 Green (positive), 🟡 Amber (neutral), 🔴 Red (negative)

### Sentiment Scores Bar Chart
- Displays sentiment score for each headline
- Horizontal bar chart for easy comparison
- Bars color-coded by sentiment category
- Range: -1.0 (very negative) to +1.0 (very positive)

## 🔧 Troubleshooting

### "ERROR: NEWS_API_KEY not set in .env file"
- **Solution**: Ensure `.env` file exists in project root and contains valid `NEWS_API_KEY`

### "ERROR: GEMINI_API_KEY not set in .env file"
- **Solution**: Ensure `.env` file contains valid `GEMINI_API_KEY`

### "Rate limit exceeded"
- **Solution**: You've exceeded NewsAPI's free tier limit. Wait before making new requests or upgrade your plan

### "Failed to connect to NewsAPI"
- **Solution**: Check internet connection and verify API key is valid

### "Streamlit not found"
- **Solution**: Run `pip install streamlit` or reinstall dependencies: `pip install -r requirements.txt`

### No headlines returned
- **Solution**: Try a different, more common topic. Some very specific topics might not return results

## 📋 Requirements

See `requirements.txt` for exact versions. Key requirements:

```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
requests>=2.31.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional sentiment visualization types
- Support for multiple languages
- Sentiment filtering and sorting
- Historical trend analysis
- Additional news sources beyond NewsAPI
- Unit tests and integration tests
- Performance optimizations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⭐ Show Your Support

If you found this project helpful, please consider:
- Giving it a ⭐ star on GitHub
- Sharing it with others
- Contributing improvements

## 📧 Contact & Support

For questions, suggestions, or issues:
- Open an [GitHub Issue](https://github.com/yourusername/news-sentiment-tracker/issues)
- Check existing issues for common problems
- Include error messages and steps to reproduce

## 🗂️ Related Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🎓 Learning Resources

This project demonstrates:
- Building interactive web apps with Streamlit
- API integration and error handling
- Data visualization with Plotly
- Environment variable management
- Sentiment analysis using LLMs
- Data processing with Pandas

Perfect for learning full-stack web development, APIs, and AI integration!

## 📊 Project Statistics

- **Lines of Code**: ~350
- **Dependencies**: 7
- **API Integrations**: 2 (NewsAPI + Google Gemini)
- **Visualizations**: 2 (Pie + Bar charts)
- **Functions**: 6+ with docstrings
- **Error Handling**: Comprehensive

## 🚀 Future Enhancements

Potential features for future versions:
- [ ] Historical sentiment tracking over time
- [ ] Support for additional languages
- [ ] Multi-source news aggregation
- [ ] Sentiment alert system
- [ ] Advanced filtering and sorting
- [ ] User accounts and saved analyses
- [ ] Mobile app version
- [ ] Sentiment trend predictions
- [ ] Custom sentiment categories
- [ ] News source credibility scoring

## ⚖️ API Rate Limits

### NewsAPI (Free Tier)
- 100 requests per day
- 50 concurrent requests
- Data from last 30 days

### Google Gemini API (Free Tier)
- 60 requests per minute
- 2,000 requests per day

Check official documentation for latest limits.

---

**Made with ❤️ by News Sentiment Tracker Team**

*Last Updated: April 2026*
