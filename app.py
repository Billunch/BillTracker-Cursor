import logging
# ... existing code ...
# print("API KEY:", CONGRESS_API_KEY)  # 移除敏感資訊輸出
# ... existing code ...

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
    logging.warning("缺少欄位，bill number：%s", bill.get("number"))
    return "https://www.congress.gov"

# 在 main 區塊加上 logging 設定（只輸出 warning 以上）
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    app.run(host="0.0.0.0", port=10000)
