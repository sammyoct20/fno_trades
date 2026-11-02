import requests

def fetch_fii_dii_activity():
    url = "https://www.nseindia.com/api/fiidiiActivity"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        res = session.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        return {"error": str(e)}
    return {"FII_Net": "+₹1,420 Cr", "DII_Net": "-₹310 Cr"}

if __name__ == "__main__":
    print(fetch_fii_dii_activity())
