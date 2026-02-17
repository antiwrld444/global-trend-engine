import requests
import json
import os
import sys

class MarketCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_market_data(self, symbol="IBM"):
        if not self.api_key:
            return {"error": "No API Key"}
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        try:
            response = requests.get(self.base_url, params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_latest(self):
        # Метод для интеграции в main loop
        # Для начала мониторим базу: BTC, Золото, S&P500
        assets = ["BTC", "GLD", "SPY"]
        results = []
        for asset in assets:
            data = self.fetch_market_data(asset)
            if "Global Quote" in data:
                quote = data["Global Quote"]
                results.append({
                    "title": f"Market Update: {asset} is at {quote.get('05. price')}",
                    "url": "https://www.alphavantage.co/",
                    "source": "AlphaVantage"
                })
        return results
