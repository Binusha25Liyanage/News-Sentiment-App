"""Editorial Intelligence Dashboard - News Sentiment Tracker."""

import html
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

from news_fetcher import get_news
from sentiment_analyzer import analyze_sentiment

st.set_page_config(
    layout="wide",
    page_title="Editorial Intelligence",
    page_icon="📡",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
body, .stApp { background-color: #0F0F0F !important; color: #FFFFFF; font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] { background-color: #141414 !important; border-right: 1px solid #2A2A2A !important; width: 200px !important; }
section[data-testid="stSidebar"] * { color: #888888 !important; }
.stTextInput > div > div > input { background: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #2A2A2A !important; border-radius: 4px !important; font-size: 13px !important; }
.stButton > button, .stDownloadButton > button { background: #CC2200 !important; color: #FFFFFF !important; border: none !important; border-radius: 4px !important; font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important; font-size: 12px !important; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #AA1A00 !important; }
div[data-testid="metric-container"] { background: #1A1A1A !important; border: 1px solid #2A2A2A !important; border-radius: 4px !important; padding: 20px !important; }
footer, #MainMenu, header { visibility: hidden !important; }
.stDataFrame { background: #1A1A1A !important; }
hr { border-color: #2A2A2A !important; }

.sidebar-card { background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 4px; padding: 12px; margin-top: 12px; }
.nav-item { background: #1A1A1A; border: 1px solid #2A2A2A; border-left: 3px solid transparent; border-radius: 2px; padding: 8px 10px; margin: 6px 0; font-size: 12px; letter-spacing: 0.8px; text-transform: uppercase; color: #888888; }
.nav-item.active { border-left-color: #CC2200; color: #FFFFFF; }
.top-navbar { background: #1A1A1A; border-bottom: 2px solid #CC2200; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.top-nav-center { display: flex; gap: 20px; font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; }
.top-nav-center span { color: #888888; }
.top-nav-center .active { color: #FFFFFF; border-bottom: 2px solid #CC2200; padding-bottom: 3px; }
.search-card { background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 4px; padding: 16px; margin-bottom: 14px; }
.chip-wrap { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.trend-chip { background: #252525; border: 1px solid #333333; border-radius: 2px; color: #AAAAAA; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; text-decoration: none; padding: 6px 8px; }
.metric-card { background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 4px; padding: 14px; }
.metric-label { color: #555555; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
.metric-value { font-size: 26px; font-weight: 700; margin: 6px 0 10px; }
.progress-track { width: 100%; height: 4px; background: #2A2A2A; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; }
.section-title { font-size: 12px; letter-spacing: 1.2px; text-transform: uppercase; color: #FFFFFF; display: flex; align-items: center; gap: 8px; }
.red-bullet { width: 6px; height: 6px; border-radius: 50%; background: #CC2200; display: inline-block; }
.magnitude-box { background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 4px; padding: 12px; max-height: 420px; overflow: auto; }
.mag-row { margin-bottom: 14px; }
.mag-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.mag-title { font-size: 10px; letter-spacing: 0.8px; text-transform: uppercase; color: #FFFFFF; }
.mag-score { font-weight: 700; font-size: 12px; }
.feed-wrap { border: 1px solid #2A2A2A; border-radius: 4px; overflow: hidden; }
.feed-header { display: grid; grid-template-columns: 1.2fr 3fr 1.2fr 3fr; background: #141414; color: #555555; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #2A2A2A; padding: 10px; }
.feed-row { display: grid; grid-template-columns: 1.2fr 3fr 1.2fr 3fr; padding: 12px 10px; border-bottom: 1px solid #2A2A2A; gap: 10px; }
.feed-row:nth-child(even) { background: #141414; }
.feed-row:nth-child(odd) { background: #1A1A1A; }
.source-badge { display: inline-block; min-width: 32px; text-align: center; background: #2A1612; border: 1px solid #CC2200; color: #CC2200; border-radius: 3px; padding: 2px 4px; font-size: 9px; font-weight: 700; }
.pill { display: inline-block; font-size: 10px; letter-spacing: 0.8px; border-radius: 999px; padding: 4px 10px; text-transform: uppercase; }
.pill.pos { background: rgba(0,200,150,0.2); color: #00C896; border: 1px solid #00C896; }
.pill.neu { background: rgba(136,136,136,0.2); color: #888888; border: 1px solid #888888; }
.pill.neg { background: rgba(204,34,0,0.2); color: #CC2200; border: 1px solid #CC2200; }
</style>
""",
    unsafe_allow_html=True,
)


def _init_state():
    """Initialize required session state keys."""
    st.session_state.setdefault("topic", "")
    st.session_state.setdefault("results", [])
    st.session_state.setdefault("stats", {"total": 0, "positive": 0, "neutral": 0, "negative": 0})
    st.session_state.setdefault("error", "")


def _escape(text):
    """Escape text for safe HTML rendering."""
    return html.escape(str(text or ""))


def _source_abbr(source):
    """Generate a 2-3 character source abbreviation."""
    cleaned = "".join(ch for ch in source if ch.isalnum() or ch.isspace()).strip()
    if not cleaned:
        return "SRC"
    parts = cleaned.split()
    if len(parts) >= 2:
        return (parts[0][:1] + parts[1][:2]).upper()
    return cleaned[:3].upper()


def _compute_stats(df):
    """Compute sentiment count summary for the dashboard."""
    total = len(df)
    positive = int((df["sentiment"] == "positive").sum()) if total else 0
    neutral = int((df["sentiment"] == "neutral").sum()) if total else 0
    negative = int((df["sentiment"] == "negative").sum()) if total else 0
    return {"total": total, "positive": positive, "neutral": neutral, "negative": negative}


def _run_analysis(topic):
    """Fetch articles and analyze sentiment for each headline."""
    with st.spinner("SCANNING GLOBAL INTELLIGENCE FEEDS..."):
        articles = get_news(topic, count=10)
        if not articles:
            st.session_state.error = "Could not fetch news articles. Please verify NEWS_API_KEY and your NewsAPI quota."
            return

        rows = []
        for article in articles:
            sentiment = analyze_sentiment(article.get("title", ""))
            rows.append(
                {
                    "source": article.get("source", "Unknown"),
                    "headline": article.get("title", "Untitled"),
                    "description": article.get("description", ""),
                    "url": article.get("url", "#"),
                    "publishedAt": article.get("publishedAt", ""),
                    "sentiment": sentiment.get("sentiment", "neutral"),
                    "score": int(sentiment.get("score", 0)),
                    "reason": sentiment.get("reason", "No contextual reason available."),
                }
            )

        st.session_state.results = rows
        st.session_state.stats = _compute_stats(pd.DataFrame(rows))
        st.session_state.error = ""


def _pdf_safe(text):
    """Convert text to a PDF-safe latin-1 string."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


def _build_pdf_report(topic, results, stats):
    """Build a PDF report from current session data and return bytes."""
    if FPDF is None:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _pdf_safe("Editorial Intelligence Report"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, _pdf_safe(f"Topic: {topic or 'N/A'}"), ln=True)
    pdf.cell(0, 7, _pdf_safe(f"Generated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"), ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, _pdf_safe("Session Summary"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, _pdf_safe(f"Total Reports: {stats.get('total', 0)}"), ln=True)
    pdf.cell(0, 7, _pdf_safe(f"Positive: {stats.get('positive', 0)}"), ln=True)
    pdf.cell(0, 7, _pdf_safe(f"Neutral: {stats.get('neutral', 0)}"), ln=True)
    pdf.cell(0, 7, _pdf_safe(f"Negative: {stats.get('negative', 0)}"), ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, _pdf_safe("Headlines"), ln=True)

    for idx, row in enumerate(results, start=1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, _pdf_safe(f"{idx}. {row.get('headline', 'Untitled')}"))
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(
            0,
            5,
            _pdf_safe(
                f"Source: {row.get('source', 'Unknown')} | Sentiment: {row.get('sentiment', 'neutral').upper()} | "
                f"Score: {row.get('score', 0)}"
            ),
        )
        pdf.multi_cell(0, 5, _pdf_safe(f"Reason: {row.get('reason', 'No contextual reason available.')}"))
        url = row.get("url", "")
        if url and url != "#":
            pdf.multi_cell(0, 5, _pdf_safe(f"URL: {url}"))
        pdf.ln(2)

    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)
    elif isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin-1", "replace")
    return pdf_bytes


def _render_sidebar():
    """Render the editorial navigation sidebar."""
    stats = st.session_state.stats
    with st.sidebar:
        st.markdown(
            """
            <div style="font-size:10px; letter-spacing:1.4px; text-transform:uppercase; color:#555555; margin-top:4px;">
                Intelligence System <span style="color:#CC2200;">●</span>
            </div>
            <div style="font-size:18px; color:#FFFFFF; font-weight:700; margin-top:4px;">Editorial Intel</div>
            <div style="font-size:10px; letter-spacing:1px; text-transform:uppercase; color:#555555; margin-top:4px;">Global Sentiment Node</div>
            """,
            unsafe_allow_html=True,
        )

        nav_items = [
            ("📡  LIVE FEED", True),
            ("📊  MARKET PULSE", False),
            ("🌐  SECTOR ANALYSIS", False),
            ("🕐  HISTORICAL SENTIMENT", False),
            ("⭐  WATCHLIST", False),
        ]
        for label, active in nav_items:
            active_class = " active" if active else ""
            st.markdown(f"<div class='nav-item{active_class}'>{_escape(label)}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="sidebar-card">
                <div style="font-size:10px; color:#555555; letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;">Live Session Stats</div>
                <div style="display:flex; justify-content:space-between;"><span>Total Scanned</span><span style="color:#FFFFFF;">{stats['total']}</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Positive</span><span style="color:#00C896;">{stats['positive']}</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Neutral</span><span style="color:#888888;">{stats['neutral']}</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Negative</span><span style="color:#CC2200;">{stats['negative']}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.session_state.results:
            pdf_data = _build_pdf_report(st.session_state.topic, st.session_state.results, stats)
            if pdf_data:
                st.download_button(
                    "GENERATE REPORT",
                    data=BytesIO(pdf_data),
                    file_name=f"editorial_intelligence_{(st.session_state.topic or 'report').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("GENERATE REPORT", use_container_width=True, disabled=True)
                st.caption("Install fpdf2 to enable PDF export: pip install fpdf2")
        else:
            st.button("GENERATE REPORT", use_container_width=True, disabled=True)
        st.markdown("<div style='margin-top:10px; font-size:11px; color:#555555;'>Help Center</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='margin-top:8px; font-size:9px; letter-spacing:1px; color:#555555; text-transform:uppercase;'>Powered by Gemini AI</div>",
            unsafe_allow_html=True,
        )


def _render_top_navbar():
    """Render the top navigation bar."""
    st.markdown(
        """
        <div class="top-navbar">
            <div style="font-weight:800; color:#FFFFFF; letter-spacing:1px;">EDITORIAL INTELLIGENCE</div>
            <div class="top-nav-center">
                <span class="active">DASHBOARD</span>
                <span>REPORTS</span>
                <span>ARCHIVE</span>
            </div>
            <div style="color:#888888; display:flex; gap:12px; align-items:center;">
                <span>🔔</span>
                <span>⚙️</span>
                <span style="width:22px; height:22px; border-radius:50%; background:#2A2A2A; display:inline-flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:11px;">U</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metrics(stats):
    """Render KPI metrics row with progress bars."""
    total = max(stats["total"], 1)
    items = [
        ("TOTAL REPORTS", stats["total"], "#FFFFFF", "#555555", (stats["total"] / total) * 100),
        ("POSITIVE SENTIMENT", stats["positive"], "#00C896", "#00C896", (stats["positive"] / total) * 100),
        ("NEUTRAL OUTLOOK", stats["neutral"], "#FFFFFF", "#888888", (stats["neutral"] / total) * 100),
        ("NEGATIVE SIGNAL", stats["negative"], "#CC2200", "#CC2200", (stats["negative"] / total) * 100),
    ]

    cols = st.columns(4)
    for idx, (label, value, value_color, bar_color, width) in enumerate(items):
        cols[idx].markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{value_color};">{value}</div>
                <div class="progress-track"><div class="progress-fill" style="width:{min(100, width):.1f}%; background:{bar_color};"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_distribution_chart(df):
    """Render donut chart for sentiment distribution."""
    sentiment_order = ["positive", "neutral", "negative"]
    sentiment_labels = ["POS", "NEU", "NEG"]
    values = [int((df["sentiment"] == s).sum()) for s in sentiment_order]

    total = sum(values) or 1
    dominant_idx = values.index(max(values)) if values else 1
    dominant_pct = (values[dominant_idx] / total) * 100

    fig = go.Figure(
        data=[
            go.Pie(
                values=values,
                labels=sentiment_labels,
                hole=0.6,
                marker=dict(colors=["#00C896", "#555555", "#CC2200"]),
                textinfo="none",
                sort=False,
            )
        ]
    )

    fig.update_layout(
        paper_bgcolor="#1A1A1A",
        plot_bgcolor="#1A1A1A",
        margin=dict(l=10, r=10, t=10, b=40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(color="#888888", size=10),
        ),
        annotations=[
            dict(
                text=f"<b>{dominant_pct:.1f}%</b><br>{sentiment_labels[dominant_idx]}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(color="#FFFFFF", size=14),
            )
        ],
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_magnitude_rows(df):
    """Render headline sentiment magnitudes with HTML bars."""
    chunks = []
    for _, row in df.iterrows():
        score = int(row["score"])
        color = "#00C896" if score > 0 else "#CC2200" if score < 0 else "#888888"
        bar_color = color
        width = min(100, abs(score))
        sign = "+" if score > 0 else ""
        chunks.append(
            f"""
            <div class="mag-row">
                <div class="mag-head">
                    <div class="mag-title">{_escape(str(row['headline'])[:90])}</div>
                    <div class="mag-score" style="color:{color};">{sign}{score:.1f}</div>
                </div>
                <div class="progress-track" style="margin-top:6px;"><div class="progress-fill" style="width:{width}%; background:{bar_color};"></div></div>
            </div>
            """
        )
    st.markdown(f"<div class='magnitude-box'>{''.join(chunks) if chunks else '<div style=\"color:#555555;\">No rows available.</div>'}</div>", unsafe_allow_html=True)


def _render_feed(df):
    """Render the intelligent headlines feed table-style layout."""
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px; margin-bottom:8px;">
            <div style="font-size:14px; letter-spacing:1px; text-transform:uppercase; color:#FFFFFF; font-weight:700;">Intelligent Headlines Feed</div>
            <div style="color:#888888;">⚲ ⭳</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows_html = []
    for _, row in df.iterrows():
        sentiment = row["sentiment"]
        if sentiment == "positive":
            pill = "<span class='pill pos'>Positive</span>"
        elif sentiment == "negative":
            pill = "<span class='pill neg'>Negative</span>"
        else:
            pill = "<span class='pill neu'>Neutral</span>"

        source = _escape(row["source"])
        abbr = _source_abbr(source)
        headline = _escape(str(row["headline"])[:140])
        reason = _escape(row["reason"])

        rows_html.append(
            f"""
            <div class="feed-row">
                <div>
                    <span class="source-badge">{abbr}</span>
                    <div style="margin-top:6px; color:#888888; font-size:10px;">{source}</div>
                </div>
                <div style="color:#FFFFFF; font-size:13px; line-height:1.35;">{headline}</div>
                <div>{pill}</div>
                <div style="color:#888888; font-size:11px; line-height:1.35;">{reason}</div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="feed-wrap">
            <div class="feed-header">
                <div>Source</div><div>Headline</div><div>Sentiment</div><div>Contextual Reason</div>
            </div>
            {''.join(rows_html) if rows_html else '<div class="feed-row"><div style="grid-column:1/-1;color:#555555;">No intelligence loaded yet.</div></div>'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='text-align:center; color:#888888; text-transform:uppercase; letter-spacing:1px; font-size:11px; margin-top:12px;'>Load More Global Intelligence</div>",
        unsafe_allow_html=True,
    )


def main():
    """Run the full Streamlit application."""
    _init_state()

    selected_chip = st.query_params.get("chip", "")
    if selected_chip:
        st.session_state.topic = str(selected_chip)
        st.query_params.clear()
        st.rerun()

    _render_sidebar()
    _render_top_navbar()

    header_col_left, header_col_right = st.columns([3, 1])
    with header_col_left:
        st.markdown("<div style='font-size:10px; color:#555555; letter-spacing:1.2px; text-transform:uppercase;'>Market Sentiment Engine</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:34px; color:#FFFFFF; font-weight:700; margin-top:2px;'>News Sentiment Tracker</div>", unsafe_allow_html=True)
    with header_col_right:
        st.markdown("<div style='font-size:10px; color:#555555; letter-spacing:1px; text-transform:uppercase; text-align:right;'>Last Global Sync</div>", unsafe_allow_html=True)
                components.html(
                        """
                        <div id="utc-clock" style="text-align:right; color:#FFFFFF; font-size:24px; font-weight:700;">--:--:-- UTC</div>
                        <script>
                        const clockNode = document.getElementById('utc-clock');
                        function tickUtcClock() {
                            const now = new Date();
                            const hh = String(now.getUTCHours()).padStart(2, '0');
                            const mm = String(now.getUTCMinutes()).padStart(2, '0');
                            const ss = String(now.getUTCSeconds()).padStart(2, '0');
                            clockNode.textContent = `${hh}:${mm}:${ss} UTC`;
                        }
                        tickUtcClock();
                        setInterval(tickUtcClock, 1000);
                        </script>
                        """,
                        height=42,
                )

    st.markdown("<div class='search-card'>", unsafe_allow_html=True)
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        topic_input = st.text_input(
            "",
            value=st.session_state.topic,
            placeholder="Search any topic (e.g., 'Global Semiconductor Shortage' or 'Renewable Energy Lea...)",
            key="topic_input_box",
        )
    with btn_col:
        analyze_clicked = st.button("ANALYZE NEWS", use_container_width=True)

    st.markdown("<div style='font-size:10px; color:#555555; letter-spacing:1px; text-transform:uppercase;'>Suggested Trends:</div>", unsafe_allow_html=True)
    chips = [
        "TECH REGULATION",
        "EV MARKET",
        "INTEREST RATES",
        "CRYPTO ADOPTION",
        "AI SAFETY",
        "DIALOG AXIATA",
        "SPACE TECH",
        "CLIMATE POLICY",
        "QUANTUM COMPUTING",
        "GLOBAL TRADE",
    ]
    chip_html = "".join([f"<a class='trend-chip' href='?chip={c.replace(' ', '+')}'>{_escape(c)}</a>" for c in chips])
    st.markdown(f"<div class='chip-wrap'>{chip_html}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked:
        st.session_state.topic = topic_input.strip()
        if not st.session_state.topic:
            st.session_state.error = "Please enter a valid topic."
        else:
            _run_analysis(st.session_state.topic)

    if st.session_state.error:
        st.error(st.session_state.error)

    result_df = pd.DataFrame(st.session_state.results)
    _render_metrics(st.session_state.stats)

    chart_col_left, chart_col_right = st.columns([1, 1.2])
    with chart_col_left:
        st.markdown("<div class='section-title'><span class='red-bullet'></span>Distribution of Sentiment</div>", unsafe_allow_html=True)
        if result_df.empty:
            st.markdown("<div style='background:#1A1A1A;border:1px solid #2A2A2A;border-radius:4px;padding:24px;color:#555555;'>No sentiment distribution yet.</div>", unsafe_allow_html=True)
        else:
            _render_distribution_chart(result_df)

    with chart_col_right:
        st.markdown("<div class='section-title'><span class='red-bullet'></span>Sentiment Magnitude by Headline</div>", unsafe_allow_html=True)
        if result_df.empty:
            st.markdown("<div style='background:#1A1A1A;border:1px solid #2A2A2A;border-radius:4px;padding:24px;color:#555555;'>No headline magnitude data yet.</div>", unsafe_allow_html=True)
        else:
            _render_magnitude_rows(result_df)

    _render_feed(result_df)

if __name__ == "__main__":
    main()
