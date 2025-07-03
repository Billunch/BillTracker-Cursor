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

def fetch_bill_detail(congress, bill_type, bill_number):
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type.lower()}/{bill_number}"
    params = {"api_key": CONGRESS_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_bill_text_html_url(congress, bill_type, bill_number):
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type.lower()}/{bill_number}/text"
    params = {"api_key": CONGRESS_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    versions = data.get("textVersions", [])
    if versions:
        latest = versions[0]
        for fmt in latest.get("formats", []):
            if fmt.get("type") == "HTML":
                return fmt.get("url")
    return None

def get_congress_gov_url(bill):
    congress = bill.get("congress")
    bill_type = bill.get("type")
    bill_number = bill.get("number")
    bill_type_map = {
        "HR": "house-bill",
        "S": "senate-bill",
        "JRES": "joint-resolution",
        "HRES": "house-resolution",
        "SRES": "senate-resolution",
        "HCONRES": "house-concurrent-resolution",
        "SCONRES": "senate-concurrent-resolution"
    }
    bill_type_str = bill_type_map.get(bill_type.upper(), bill_type.lower()) if bill_type else None

    if congress and bill_type_str and bill_number:
        return f"https://www.congress.gov/bill/{congress}th-congress/{bill_type_str}/{bill_number}"
    print("缺少欄位，bill內容：", bill)
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
            congress = bill.get("congress")
            bill_type = bill.get("type")
            bill_number = bill.get("number")
            summary = ""
            html_url = None
            # 取得法案摘要與 HTML 原文連結
            if congress and bill_type and bill_number:
                try:
                    detail = fetch_bill_detail(congress, bill_type, bill_number)
                    summary = detail.get("bill", {}).get("summary", {}).get("text", "")
                except Exception as e:
                    summary = ""
                try:
                    html_url = fetch_bill_text_html_url(congress, bill_type, bill_number)
                except Exception as e:
                    html_url = None
            url = get_congress_gov_url(bill)
            msg = f"*新法律通過！*\n{title}\n\n{summary}\n[查看法案]({url})"
            if html_url:
                msg += f"\n[法案原文（HTML）]({html_url})"
            send_telegram_message(msg)
        return jsonify({"status": "ok", "message": "Notification sent!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
