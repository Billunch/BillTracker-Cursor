from flask import Flask, request, jsonify
import requests
import os
import re

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

def fetch_bill_text(congress, bill_type, bill_number):
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
                # 取得 HTML 內容網址
                return fmt.get("url")
    return None

def extract_effective_date_from_summary(summary):
    # 嘗試從摘要中找生效日關鍵字
    if not summary:
        return "未明確規定"
    match = re.search(r"(take effect.*?\.|effective date.*?\.)", summary, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return "未明確規定"

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
    print("缺少欄位，bill number：", bill.get("number"))
    return "https://www.congress.gov"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
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
            effective_date = "未明確規定"
            if congress and bill_type and bill_number:
                try:
                    detail = fetch_bill_detail(congress, bill_type, bill_number)
                    summary = detail.get("bill", {}).get("summary", {}).get("text", "")
                    effective_date = extract_effective_date_from_summary(summary)
                except Exception as e:
                    summary = ""
            url = get_congress_gov_url(bill)
            msg = (
                "*新法律通過！*\n"
                f"法案名稱: {title}\n"
                f"生效時間: {effective_date}\n"
                f"法案摘要: {summary}\n"
                f"法案網址連結: {url}"
            )
            send_telegram_message(msg)
        return jsonify({"status": "ok", "message": "Notification sent!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
