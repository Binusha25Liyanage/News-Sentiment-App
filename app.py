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

# Add custom CSS for dark-ish sidebar and styling
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #2c2f33;
        color: #ffffff;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }
    [data-testid="stSidebar"] .css-qri22k {
        color: #ffffff;
    }
    .sentiment-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        display: inline-block;
    }
    .sentiment-positive {
        background-color: #2ecc71;
        color: #ffffff;
    }
    .sentiment-neutral {
        background-color: #f39c12;
        color: #ffffff;
    }
    .sentiment-negative {
        background-color: #e74c3c;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

def get_sentiment_color_name(sentiment):
    """
    Get color name for sentiment.
    
    Args:
        sentiment (str): The sentiment type ("positive", "neutral", "negative")
    
    Returns:
        str: Sentiment label for display
    """
    return "🟢 Positive" if sentiment == "positive" else \
           "🟡 Neutral" if sentiment == "neutral" else \
           "🔴 Negative" if sentiment == "negative" else "❓ Error"


def main():
    """Main application function - Streamlit app logic."""
    
    # Initialize session state for storing articles data
    if "articles_data" not in st.session_state:
        st.session_state.articles_data = None
    
    # Sidebar with dark styling
    with st.sidebar:
        st.markdown("## 📰 News Sentiment Tracker")
        st.markdown("""
        Track and analyze the sentiment of trending news headlines in real-time 
        using AI-powered sentiment analysis.
        """)
        
        st.divider()
        
        # Display live statistics if data exists
        if st.session_state.articles_data is not None:
            df = st.session_state.articles_data
            df_valid = df[df["Sentiment"] != "error"]
            
            if len(df_valid) > 0:
                st.markdown("### 📊 Live Statistics")
                
                total = len(df_valid)
                positive = len(df_valid[df_valid["Sentiment"] == "positive"])
                neutral = len(df_valid[df_valid["Sentiment"] == "neutral"])
                negative = len(df_valid[df_valid["Sentiment"] == "negative"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Articles", total)
                    st.metric("🟢 Positive", positive)
                with col2:
                    st.metric("🟡 Neutral", neutral)
                    st.metric("🔴 Negative", negative)
    
    # Main page title
    st.title("📰 News Sentiment Tracker")
    st.markdown("Analyze the sentiment of news headlines in real-time using Google Gemini AI")
    
    # Initialize session state for storing articles data
    if "articles_data" not in st.session_state:
        st.session_state.articles_data = None
    
    # Search and analyze section
    st.markdown("### 🔍 Search & Analyze")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        topic = st.text_input(
            "Enter a news topic to analyze:",
            placeholder="e.g., Tesla, Sri Lanka economy, AI, Climate change",
            key="topic_input"
        )
    
    with col2:
        analyze_button = st.button(
            "Analyze News",
            use_container_width=True,
            type="primary"
        )
    
    # Process when button is clicked
    if analyze_button:
        if not topic.strip():
            st.error("❌ Please enter a topic to analyze.")
        else:
            # Fetch and analyze news with spinner
            with st.spinner("📰 Fetching and analyzing headlines..."):
                articles = get_news(topic.strip(), count=10)
                
                if not articles:
                    st.error("❌ Could not fetch news articles. Please check your NEWS_API_KEY in .env file.")
                else:
                    # Analyze sentiment for each article
                    analyzed_articles = []
                    
                    for article in articles:
                        sentiment_data = analyze_sentiment(article["title"])
                        
                        analyzed_articles.append({
                            "Source": article["source"],
                            "Headline": article["title"],
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
            
            st.divider()
            
            # Metric cards row
            st.markdown("### 📊 Summary Metrics")
            total = len(df_valid)
            positive = len(df_valid[df_valid["Sentiment"] == "positive"])
            neutral = len(df_valid[df_valid["Sentiment"] == "neutral"])
            negative = len(df_valid[df_valid["Sentiment"] == "negative"])
            
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.metric("Total Articles", total)
            with mcol2:
                st.metric("Positive", positive, delta=f"{positive/total*100:.0f}%")
            with mcol3:
                st.metric("Neutral", neutral, delta=f"{neutral/total*100:.0f}%")
            with mcol4:
                st.metric("Negative", negative, delta=f"{negative/total*100:.0f}%")
            
            st.divider()
            
            # Charts row
            st.markdown("### 📈 Visualizations")
            col1, col2 = st.columns(2)
            
            colors_map = {
                "positive": "#2ecc71",
                "neutral": "#f39c12",
                "negative": "#e74c3c"
            }
            
            with col1:
                # Sentiment distribution pie chart
                sentiment_counts = df_valid["Sentiment"].value_counts()
                
                pie_colors = [colors_map.get(s, "#95a5a6") for s in sentiment_counts.index]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[f"🟢 {s.capitalize()}" if s == "positive" else 
                            f"🟡 {s.capitalize()}" if s == "neutral" else 
                            f"🔴 {s.capitalize()}" for s in sentiment_counts.index],
                    values=sentiment_counts.values,
                    marker=dict(colors=pie_colors),
                    textposition="inside",
                    textinfo="label+percent"
                )])
                
                fig_pie.update_layout(
                    title="Sentiment Distribution",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Sentiment scores bar chart
                df_sorted = df_valid.sort_values("Score", ascending=True).reset_index(drop=True)
                df_sorted["Headline_Short"] = df_sorted["Headline"].str[:40] + "..."
                
                bar_colors = [colors_map.get(s, "#95a5a6") for s in df_sorted["Sentiment"]]
                
                fig_bar = go.Figure(data=[go.Bar(
                    y=df_sorted["Headline_Short"],
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
                    margin=dict(l=250)
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            # Results table
            st.markdown("### 📑 Detailed Results")
            
            # Create table dataframe with formatted columns
            table_df = pd.DataFrame()
            table_df["Source"] = df_valid["Source"]
            table_df["Headline"] = df_valid["Headline"].str[:70] + "..."
            table_df["URL"] = df_valid["URL"]
            table_df["Sentiment"] = df_valid["Sentiment"].apply(get_sentiment_color_name)
            table_df["Score"] = df_valid["Score"].round(2)
            table_df["Reason"] = df_valid["Reason"]
            
            # Display using st.dataframe with color styling
            st.dataframe(
                table_df[["Source", "Headline", "Sentiment", "Score", "Reason"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.NumberColumn(format="%.2f"),
                }
            )
            
            # Download button
            csv = df_valid[["Source", "Headline", "Sentiment", "Score", "Reason", "Published"]].to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"sentiment_analysis_{topic.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
