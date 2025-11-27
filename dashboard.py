import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURATION
# 🔴 REPLACE THIS with your actual Terraform Output URL
API_URL = "https://g6r2etqn5hygjhv4lpohro46mu0ibzfd.lambda-url.eu-central-1.on.aws/ "

st.set_page_config(page_title="Meme Coin Index", page_icon="🐸", layout="centered")

# --- HEADER ---
st.title("🐸 Pepe Fear & Greed Index")
st.markdown("Real-time volatility and momentum tracking for $PEPE, powered by **AWS Lambda** and **Terraform**.")

# --- FETCH DATA ---
@st.cache_data(ttl=60) # Cache for 1 min to save API calls
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to AWS API: {e}")
        return None

data = fetch_data()

if data:
    # --- METRICS ROW ---
    col1, col2, col3 = st.columns(3)
    
    score = data.get("index_score", 50)
    sentiment = data.get("sentiment", "Neutral")
    timestamp = data.get("timestamp", str(datetime.now()))

    # Color Logic
    color = "red" if score < 25 else "green" if score > 75 else "orange"
    
    with col1:
        st.metric(label="Current Score", value=f"{score}/100", delta=None)
    with col2:
        st.metric(label="Sentiment", value=sentiment)
        st.caption(f"Last Updated: {timestamp}")
    
    # --- GAUGE CHART ---
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Fear vs Greed"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "orangered"},
                {'range': [25, 75], 'color': "lightgray"},
                {'range': [75, 100], 'color': "lightgreen"}],
        }
    ))
    st.plotly_chart(fig)

    # --- RAW DATA (For Engineers) ---
    with st.expander("See Raw JSON Response"):
        st.json(data)
        
    st.markdown("---")
    st.markdown("### 🏗️ Architecture")
    st.caption("Built with AWS Lambda, Docker, DynamoDB, and Terraform.")