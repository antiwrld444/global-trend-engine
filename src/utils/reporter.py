import requests
import json

class TelegramReporter:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    def send_alert(self, message):
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(self.api_url, json=payload)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

# Пример интеграции будет добавлен в main.py на следующем шаге
