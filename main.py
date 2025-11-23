import os
import requests
import numpy as np
import json
from datetime import datetime, timedelta

# CONFIGURATION
COIN_ID = os.getenv('COIN_ID', 'pepe') 
CURRENCY = 'usd'
DAYS = '30'
CACHE_DURATION_MINUTES = 5

# GLOBAL CACHE (Persists while Lambda container is warm)
_CACHE = {
    "data": None,
    "timestamp": None
}

def fetch_market_data(coin_id):
    """Get historical price/volume data from CoinGecko (Free Tier)"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': CURRENCY, 'days': DAYS, 'interval': 'daily'}
    
    try:
        print(f"Fetching fresh data for {coin_id}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_index(data):
    prices = [p[1] for p in data['prices']]
    
    # 1. Volatility Score
    returns = np.diff(prices) / prices[:-1]
    volatility = np.std(returns)
    
    # 2. Momentum Score
    current_price = prices[-1]
    sma_30 = np.mean(prices)
    momentum = (current_price - sma_30) / sma_30
    
    base_score = 50 + (momentum * 100) 
    final_score = max(0, min(100, base_score))
    
    return int(final_score)

def get_cached_or_fresh_data():
    global _CACHE
    now = datetime.now()
    
    # Check if cache exists and is fresh
    if _CACHE["data"] and _CACHE["timestamp"]:
        time_diff = now - _CACHE["timestamp"]
        if time_diff < timedelta(minutes=CACHE_DURATION_MINUTES):
            print("Returning CACHED data")
            return _CACHE["data"]
            
    # If no cache or stale, fetch new
    data = fetch_market_data(COIN_ID)
    if data:
        _CACHE["data"] = data
        _CACHE["timestamp"] = now
    return data

def handler(event, context):
    data = get_cached_or_fresh_data()
    
    if not data:
        return {"statusCode": 500, "body": json.dumps("Failed to fetch data")}
    
    index_score = calculate_index(data)
    
    result = {
        "coin": COIN_ID,
        "index_score": index_score,
        "sentiment": "Extreme Greed" if index_score > 75 else "Fear" if index_score < 25 else "Neutral",
        "timestamp": datetime.now().isoformat(),
        "note": "Raw Alpha v1.0"
    }
    
    return {
        "statusCode": 200, 
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # Allows frontend to call it later
        },
        "body": json.dumps(result)
    }