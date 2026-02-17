import requests
import json
import os

class DeepSearchCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"

    def search(self, query, search_depth="advanced"):
        if not self.api_key:
            return {"error": "No Tavily API Key"}
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": True,
            "max_results": 5
        }
        try:
            response = requests.post(self.base_url, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_latest(self):
        # Автоматический поиск по самым горячим темам дня для расширения базы
        # Например: "global market trends 2026", "AI breakthrough today"
        queries = ["emerging consumer trends 2026", "major tech shifts today"]
        results = []
        for q in queries:
            data = self.search(q)
            if "results" in data:
                for res in data["results"]:
                    results.append({
                        "title": res["title"],
                        "url": res["url"],
                        "source": "Tavily Deep Search"
                    })
        return results
