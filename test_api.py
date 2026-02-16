import requests
import json

def test_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=f5cce9001dac4f7f8bc45afeb94d5c89"
    r = requests.get(url)
    return r.status_code == 200

def test_alpha():
    url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=X6S15Y2LFV0MRLWX"
    r = requests.get(url)
    return "Global Quote" in r.text

print(json.dumps({"newsapi": test_news(), "alphavantage": test_alpha()}))
