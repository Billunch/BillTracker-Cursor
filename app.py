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
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("bills", [])

def get_congress_gov_url(bill):
    congress = bill.get("congress")
    bill_type = bill.get("billType")
    bill_number = bill.get("billNumber")
    bill_type_map = {
        "hr": "house-bill",
        "s": "senate-bill",
        "jres": "joint-resolution",
        "hres": "house-resolution",
        "sres": "senate-resolution",
        "hconres": "house-concurrent-resolution",
        "sconres": "senate-concurrent-resolution"
    }
    if bill_type:
        bill_type_str = bill_type_map.get(bill_type.lower(), bill_type)
    else:
        bill_type_str = None
    if congress and bill_type_str and bill_number:
        return f"https://www.congress.gov/bill/{congress}th-congress/{bill_type_str}/{bill_number}"
    return "https://www.congress.gov"

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
            url = get_congress_gov_url(bill)
            msg = f"*新法律通過！*\n{title}\n[查看法案]({url})"
            send_telegram_message(msg)
        return jsonify({"status": "ok", "message": "Notification sent!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
