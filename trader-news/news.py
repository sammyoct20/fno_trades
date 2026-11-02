def fetch_market_news_sentiment():
    news_headlines = [
        {"title": "RBI keeps repo rate unchanged; banking stocks surge.", "sentiment": "BULLISH"},
        {"title": "F&O expiry day volatility expected as heavy open interest builds up.", "sentiment": "NEUTRAL"}
    ]
    return news_headlines

if __name__ == "__main__":
    print(fetch_market_news_sentiment())
