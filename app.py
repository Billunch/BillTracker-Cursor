你遇到的狀況是：**每則訊息的「查看法案」連結都一樣**，這代表 `get_congress_gov_url(bill)` 回傳的網址 fallback 到 `https://www.congress.gov`，而不是每個法案的專屬頁面。

---

## 主要原因
這通常是因為 API 回傳的 bill 物件裡，`congress`、`billType` 或 `billNumber` 欄位有缺漏，導致組合網址時失敗。

---

## 解決步驟

### 1. 印出 bill 物件內容 debug

請在 `for bill in bills:` 迴圈裡加上：
```python
print(bill)
```
然後在 Render 的 log 裡觀察每個 bill 的內容，確認正確的欄位名稱。

---

### 2. 根據實際欄位修正組合網址

根據 Congress.gov API 文件，bill 物件的結構可能如下（請以你實際 print 出來的為準）：

```json
{
  "billId": "s2207-119",
  "congress": "119",
  "billType": "s",
  "billNumber": "2207",
  "title": "...",
  ...
}
```
如果你發現欄位名稱不同（例如 `number` 而不是 `billNumber`），請修正對應。

---

### 3. 強化防呆與欄位對應

請將 `get_congress_gov_url` 改成如下，並在 fallback 前印出 bill 內容：

```python
def get_congress_gov_url(bill):
    congress = bill.get("congress")
    bill_type = bill.get("billType")
    bill_number = bill.get("billNumber") or bill.get("number")
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
    print("缺少欄位，bill內容：", bill)
    return "https://www.congress.gov"
```

---

### 4. 完整 app.py 片段

只需替換 `get_congress_gov_url`，其餘不變。

---

## 你應該怎麼做？

1. 重新部署後，觀察 Render log，找出 bill 物件的實際欄位名稱。
2. 根據 log，修正 `get_congress_gov_url` 取值的 key。
3. 確認每則訊息的連結都不同且正確。

---

如你願意，請貼一份 print(bill) 的 log 給我，我可以幫你精確對應正確欄位！
