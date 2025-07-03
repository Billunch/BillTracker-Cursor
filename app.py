from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CONGRESS_API_KEY = os.environ.get("CONGRESS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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
    # Debug: 印出 API 金鑰（測試用，部署時可刪除）
    print("CONGRESS_API_KEY:", CONGRESS_API_KEY)
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

@app.route("/")
def index():
    return "US Congress Law Notifier is running!"

@app.route("/trigger", methods=["POST", "GET"])
def trigger():
    try:
        bills = fetch_latest_enacted_laws()
        for bill in bills:
            title = bill.get("title", "(No Title)")
            url = bill.get("url", "https://congress.gov")
            msg = f"*新法律通過！*\n{title}\n[查看法案]({url})"
            send_telegram_message(msg)
        return jsonify({"status": "ok", "message": "Notification sent!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
