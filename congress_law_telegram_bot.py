import requests
import json
import os

CONGRESS_API_KEY = os.environ["CONGRESS_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def fetch_latest_enacted_laws():
    url = "https://api.congress.gov/v3/bill"
    params = {
        "api_key": CONGRESS_API_KEY,
        "congress": "118",
        "billType": "hr,s,jres,hres,sres,hconres,sconres",
        "enacted": "true",
        "sort": "latestActionDate:desc",
        "limit": 5
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("bills", [])

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

def main():
    bills = fetch_latest_enacted_laws()
    for bill in bills:
        title = bill.get("title", "(No Title)")
        url = bill.get("url", "https://congress.gov")
        msg = f"*新法律通過！*\n{title}\n[查看法案]({url})"
        send_telegram_message(msg)

if __name__ == "__main__":
    main()
