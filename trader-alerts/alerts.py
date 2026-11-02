def check_alert_conditions(symbol: str, current_iv: float, threshold_iv: float):
    if current_iv >= threshold_iv:
        return {"alert": True, "message": f"ALERT: Implied Volatility spike detected for {symbol} at {current_iv}%!"}
    return {"alert": False}

if __name__ == "__main__":
    print(check_alert_conditions("NIFTY 24000 CE", 28.5, 25.0))
