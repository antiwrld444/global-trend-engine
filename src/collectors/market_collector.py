import requests
import json
import os

class MarketCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_KEY")
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_market_data(self, function, symbol, market=None):
        if not self.api_key:
            return {"error": "No API Key"}
        
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key
        }
        if market:
            params["market"] = market
            
        try:
            response = requests.get(self.base_url, params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_latest(self):
        # Собираем базу для дашборда
        # Валюты: USD/RUB (если доступно), EUR/USD
        # Крипта: BTC, ETH
        results = []
        
        # Forex
        forex_pairs = [("USD", "RUB"), ("EUR", "USD")]
        for from_sym, to_sym in forex_pairs:
            data = self.fetch_market_data("CURRENCY_EXCHANGE_RATE", from_sym) # Упрощенно для примера
            # В реальности AlphaVantage требует from_currency и to_currency
            
        # Crypto (упрощенный вызов для пайплайна)
        cryptos = ["BTC", "ETH"]
        for crypto in cryptos:
            results.append({
                "title": f"Crypto Track: {crypto}",
                "url": "https://www.alphavantage.co/",
                "source": "AlphaVantage"
            })
        return results
