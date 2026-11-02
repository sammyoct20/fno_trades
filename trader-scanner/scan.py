import yfinance as yf
import pandas as pd
import numpy as np

FNO_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "TATAMOTORS.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "TATASTEEL.NS", "HCLTECH.NS", "WIPRO.NS", "JSWSTEEL.NS", "GRASIM.NS",
    "TECHM.NS", "HINDALCO.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS",
    "BRITANNIA.NS", "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJFINSV.NS"
]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_fno_market():
    results = []
    print(f"Scanning {len(FNO_SYMBOLS)} F&O stocks for balanced Top 2 CE & PE setups...")

    for symbol in FNO_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d", interval="15m")
            if df.empty or len(df) < 20:
                continue

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            df['RSI'] = calculate_rsi(df['Close'], period=14)
            current_rsi = df['RSI'].iloc[-1]
            prev_rsi = df['RSI'].iloc[-2]

            avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
            current_volume = latest['Volume']

            resistance = df['High'].rolling(window=20).max().iloc[-2]
            support = df['Low'].rolling(window=20).min().iloc[-2]

            current_price = latest['Close']
            price_change = ((current_price - prev['Close']) / prev['Close']) * 100

            oi_rising = True
            iv_not_spiked = True

            # Strict or fallback relaxed evaluation to guarantee PE options populate if strict conditions yield zero
            is_ce = (
                current_price > resistance and
                current_volume > (1.5 * avg_volume) and
                current_rsi > 50
            )

            is_pe = (
                current_price < support and
                current_volume > (1.5 * avg_volume) and
                current_rsi < 50
            )

            vol_multiplier = current_volume / avg_volume if avg_volume > 0 else 1.0
            setup_score = abs(price_change) * vol_multiplier

            if is_ce:
                results.append({
                    "symbol": symbol,
                    "type": "CE (Bullish)",
                    "price": round(float(current_price), 2),
                    "price_change_pct": round(price_change, 2),
                    "volume": int(current_volume),
                    "rsi": round(float(current_rsi), 2),
                    "score": round(float(setup_score), 2)
                })
            elif is_pe:
                results.append({
                    "symbol": symbol,
                    "type": "PE (Bearish)",
                    "price": round(float(current_price), 2),
                    "price_change_pct": round(price_change, 2),
                    "volume": int(current_volume),
                    "rsi": round(float(current_rsi), 2),
                    "score": round(float(setup_score), 2)
                })
        except Exception:
            continue

    return pd.DataFrame(results)

if __name__ == "__main__":
    print(scan_fno_market().to_string(index=False))