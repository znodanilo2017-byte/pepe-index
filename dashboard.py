import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURATION
# 🔴 REPLACE THIS with your Terraform Output URL
API_URL = "https://g6r2etqn5hygjhv4lpohro46mu0ibzfd.lambda-url.eu-central-1.on.aws/"
COIN_ID = "pepe"

# Set layout to centered for a clean, blog-post feel
st.set_page_config(page_title="Pepe Index", page_icon="🐸", layout="centered")

# --- HEADER ---
st.title("🐸 Pepe Fear & Greed Index")
st.markdown(f"""
Real-time volatility tracking for **${COIN_ID.upper()}**.  
Powered by **AWS Lambda**, **DynamoDB**, and **Terraform**.
""")

# --- HELPER FUNCTIONS ---
def get_market_chart():
    """Fetches 30-day price history from CoinGecko for context"""
    url = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/market_chart?vs_currency=usd&days=30"
    try:
        data = requests.get(url).json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return pd.DataFrame()

def get_live_score():
    """Fetches the AI Score from your AWS Lambda"""
    try:
        response = requests.get(API_URL)
        return response.json()
    except Exception as e:
        return None

# --- SECTION 1: AI SCORE ---
st.markdown("---")
st.header("🤖 AI Sentiment Score")

data = get_live_score()

if data:
    score = data.get("index_score", 50)
    sentiment = data.get("sentiment", "Neutral")
    updated = data.get("timestamp", str(datetime.now()))
    
    # 1. Big Metric Display
    st.metric(label="Current Sentiment", value=f"{score}/100", delta=sentiment)
    
    # 2. Gauge Chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "orangered"}, # Fear
                {'range': [25, 75], 'color': "lightgray"},
                {'range': [75, 100], 'color': "lightgreen"}], # Greed
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Last AI Update: {updated}")
    
    with st.expander("View Raw JSON Response"):
        st.json(data)

else:
    st.warning("⚠️ AWS Lambda is currently sleeping. Refresh in a few seconds.")

# --- SECTION 2: MARKET CONTEXT ---
st.markdown("---")
st.header("📉 Market Trend (30 Days)")

df_prices = get_market_chart()
if not df_prices.empty:
    st.line_chart(df_prices.set_index('timestamp')['price'])
    st.caption("Price data fetched live from CoinGecko.")
else:
    st.warning("Could not load price history.")

# --- FOOTER ---
st.markdown("---")
st.markdown("### 🏗️ Architecture")
st.caption("Built with AWS Lambda, Docker, DynamoDB, and Terraform.")