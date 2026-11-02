import pandas as pd

def evaluate_fno_entry_trigger(df: pd.DataFrame):
    latest = df.iloc[-1]
    if latest['Close'] > latest['VWAP'] and latest['Volume'] > latest['Avg_Volume']:
        return {"signal": "BUY_CALL_OR_FUTURE", "confidence": "HIGH"}
    elif latest['Close'] < latest['VWAP'] and latest['Volume'] > latest['Avg_Volume']:
        return {"signal": "BUY_PUT_OR_SHORT_FUTURE", "confidence": "HIGH"}
    return {"signal": "HOLD", "confidence": "LOW"}
