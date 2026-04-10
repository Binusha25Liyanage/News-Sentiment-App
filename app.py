"""
News Sentiment Tracker - Main Streamlit Application
A web dashboard to fetch news headlines and analyze their sentiment using AI.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from news_fetcher import get_news
from sentiment_analyzer import analyze_sentiment

# Configure Streamlit page settings
st.set_page_config(
    page_title="News Sentiment Tracker",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for styling
st.markdown("""
    <style>
    .sentiment-positive {
        background-color: #90EE90;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        color: #1C5E1C;
        font-weight: bold;
    }
    .sentiment-neutral {
        background-color: #D3D3D3;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        color: #333333;
        font-weight: bold;
    }
    .sentiment-negative {
        background-color: #FFB6C6;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        color: #8B0000;
        font-weight: bold;
    }
    .sentiment-error {
        background-color: #FFE4E1;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        color: #8B0000;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def get_sentiment_color(sentiment):
    """
    Get HTML color badge for sentiment display.
    
    Args:
        sentiment (str): The sentiment type ("positive", "neutral", "negative", "error")
    
    Returns:
        str: HTML styled badge
    """
    class_name = f"sentiment-{sentiment}"
    label = sentiment.capitalize()
    return f'<span class="{class_name}">{label}</span>'


def main():
    """Main application function - Streamlit app logic."""
    
    # Page title
    st.title("📰 News Sentiment Tracker")
    st.markdown("Analyze the sentiment of news headlines in real-time using AI")
    
    # Sidebar
    with st.sidebar:
        st.header("About This App")
        st.markdown("""
        **News Sentiment Tracker** helps you understand the emotional tone of news articles.
        
        ### How it works:
        1. Enter a topic you're interested in
        2. Click "Analyze News" to fetch headlines
        3. The app analyzes sentiment using Google Gemini AI
        4. View sentiment distribution and scores
        
        ### Sentiment Labels:
        - 🟢 **Positive** (score > 0.3): Optimistic or good news
        - ⚪ **Neutral** (score -0.3 to 0.3): Factual or balanced reporting
        - 🔴 **Negative** (score < -0.3): Pessimistic or concerning news
        """)
        
        st.divider()
        
        # Display statistics if data exists
        if "articles_data" in st.session_state and st.session_state.articles_data:
            st.subheader("📊 Statistics")
            
            df = st.session_state.articles_data
            total = len(df)
            positive = len(df[df["Sentiment"] == "positive"])
            neutral = len(df[df["Sentiment"] == "neutral"])
            negative = len(df[df["Sentiment"] == "negative"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Articles", total)
            with col2:
                st.metric("Analyzed", total)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🟢 Positive", positive)
            with col2:
                st.metric("⚪ Neutral", neutral)
            with col3:
                st.metric("🔴 Negative", negative)
    
    # Initialize session state for storing articles data
    if "articles_data" not in st.session_state:
        st.session_state.articles_data = None
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Topic input
        topic = st.text_input(
            "Enter a news topic to analyze:",
            placeholder="e.g., Tesla, Sri Lanka economy, AI, Climate change",
            key="topic_input"
        )
    
    with col2:
        # Analyze button
        analyze_button = st.button(
            "🔍 Analyze News",
            use_container_width=True,
            type="primary"
        )
    
    # Process when button is clicked
    if analyze_button:
        if not topic.strip():
            st.error("❌ Please enter a topic to analyze.")
        else:
            # Fetch and analyze news
            with st.spinner("⏳ Fetching headlines..."):
                articles = get_news(topic.strip(), count=10)
            
            if not articles:
                st.error("❌ Could not fetch news articles. Please check your NEWS_API_KEY in .env file.")
            else:
                # Analyze sentiment for each article
                with st.spinner("🤖 Analyzing sentiment with AI..."):
                    analyzed_articles = []
                    
                    for article in articles:
                        sentiment_data = analyze_sentiment(article["title"])
                        
                        analyzed_articles.append({
                            "Source": article["source"],
                            "Title": article["title"],
                            "URL": article["url"],
                            "Sentiment": sentiment_data["sentiment"],
                            "Score": sentiment_data["score"],
                            "Reason": sentiment_data["reason"],
                            "Published": article["publishedAt"][:10],
                            "Description": article["description"]
                        })
                
                # Store in session state
                df = pd.DataFrame(analyzed_articles)
                st.session_state.articles_data = df
    
    # Display results if data exists
    if st.session_state.articles_data is not None:
        df = st.session_state.articles_data
        
        # Filter out error entries for visualization
        df_valid = df[df["Sentiment"] != "error"]
        
        if len(df_valid) == 0:
            st.error("❌ All sentiment analyses returned errors. Please check your GEMINI_API_KEY in .env file.")
        else:
            st.divider()
            st.subheader("📈 Results")
            
            # Row 1: Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment distribution pie chart
                sentiment_counts = df_valid["Sentiment"].value_counts()
                colors = {
                    "positive": "#90EE90",
                    "neutral": "#D3D3D3",
                    "negative": "#FFB6C6"
                }
                
                pie_colors = [colors.get(s, "#CCCCCC") for s in sentiment_counts.index]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    marker=dict(colors=pie_colors),
                    textposition="inside",
                    textinfo="label+percent"
                )])
                
                fig_pie.update_layout(
                    title="Sentiment Distribution",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Sentiment scores bar chart
                df_sorted = df_valid.sort_values("Score", ascending=True)
                
                # Truncate titles for display
                df_sorted["Title_Short"] = df_sorted["Title"].str[:40] + "..."
                
                bar_colors = [colors.get(s, "#CCCCCC") for s in df_sorted["Sentiment"]]
                
                fig_bar = go.Figure(data=[go.Bar(
                    y=df_sorted["Title_Short"],
                    x=df_sorted["Score"],
                    orientation="h",
                    marker=dict(color=bar_colors),
                    text=df_sorted["Score"].round(2),
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Score: %{x:.2f}<extra></extra>"
                )])
                
                fig_bar.update_layout(
                    title="Sentiment Scores by Article",
                    height=400,
                    xaxis_title="Sentiment Score (-1.0 to 1.0)",
                    yaxis_title="",
                    showlegend=False,
                    margin=dict(l=200)
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Row 2: Articles table
            st.subheader("📑 Detailed Results")
            
            # Create display dataframe with formatted columns
            display_df = pd.DataFrame()
            display_df["Source"] = df_valid["Source"]
            display_df["Title"] = df_valid.apply(
                lambda row: f'<a href="{row["URL"]}" target="_blank">{row["Title"][:60]}...</a>',
                axis=1
            )
            display_df["Sentiment"] = df_valid["Sentiment"].apply(get_sentiment_color)
            display_df["Score"] = df_valid["Score"].apply(lambda x: f"{x:.2f}")
            display_df["Reason"] = df_valid["Reason"]
            display_df["Published"] = df_valid["Published"]
            
            # Display table
            st.write(
                display_df.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )
            
            # Add download button
            csv = df_valid[["Source", "Title", "Sentiment", "Score", "Reason", "Published"]].to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"sentiment_analysis_{st.session_state.get('topic_input', 'news')}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
