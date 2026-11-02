import requests

def fetch_nse_corporate_announcements(symbol: str):
    url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        res = session.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()[:5]
    except Exception as e:
        return {"error": str(e)}
    return {"status": f"Fetched mock filings for {symbol}"}

if __name__ == "__main__":
    print(fetch_nse_corporate_announcements("RELIANCE"))
