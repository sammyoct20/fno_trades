import time
import yfinance as yf
import pandas as pd
import numpy as np

FNO_SYMBOLS = [
    "360ONE.NS", "ABB.NS", "ABCAPITAL.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS",
    "ADANIPORTS.NS", "ADANIPOWER.NS", "ALKEM.NS", "AMBER.NS", "AMBUJACEM.NS", "ANANDRATHI.NS",
    "ANGELONE.NS", "APLAPOLLO.NS", "APOLLOHOSP.NS", "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTRAL.NS",
    "ATHERENERG.NS", "AUBANK.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJAJFINSV.NS",
    "BAJFINANCE.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BDL.NS", "BEL.NS",
    "BHARATFORG.NS", "BHARTIARTL.NS", "BHEL.NS", "BIOCON.NS", "BLUESTARCO.NS", "BOSCHLTD.NS",
    "BPCL.NS", "BRITANNIA.NS", "BSE.NS", "CAMS.NS", "CANBK.NS", "CDSL.NS", "CGPOWER.NS",
    "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS", "COCHINSHIP.NS", "COFORGE.NS", "COLPAL.NS",
    "CONCOR.NS", "CROMPTON.NS", "CUMMINSIND.NS", "DABUR.NS", "DELHIVERY.NS", "DIVISLAB.NS",
    "DIXON.NS", "DLF.NS", "DMART.NS", "DRREDDY.NS", "EICHERMOT.NS", "ENRIN.NS", "ETERNAL.NS",
    "FEDERALBNK.NS", "FORCEMOT.NS", "FORTIS.NS", "GAIL.NS", "GLENMARK.NS", "GMRAIRPORT.NS",
    "GODFRYPHLP.NS", "GODREJCP.NS", "GODREJPROP.NS", "GRASIM.NS", "GVT&D.NS", "HAL.NS",
    "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HYUNDAI.NS", "ICICIBANK.NS",
    "ICICIGI.NS", "ICICIPRULI.NS", "IDEA.NS", "IDFCFIRSTB.NS", "IEX.NS", "INDHOTEL.NS",
    "INDIANB.NS", "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFY.NS", "INOXWIND.NS", "IOC.NS",
    "IREDA.NS", "IRFC.NS", "ITC.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JSWENERGY.NS", "JSWSTEEL.NS",
    "JUBLFOOD.NS", "KALYANKJIL.NS", "KAYNES.NS", "KEI.NS", "KFINTECH.NS", "KOTAKBANK.NS",
    "KPITTECH.NS", "LAURUSLABS.NS", "LICHSGFIN.NS", "LICI.NS", "LODHA.NS", "LT.NS", "LTF.NS",
    "LTM.NS", "LUPIN.NS", "M&M.NS", "MAHABANK.NS", "MANAPPURAM.NS", "MANKIND.NS", "MARICO.NS",
    "MARUTI.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "MCX.NS", "MFSL.NS", "MOTHERSON.NS", "MOTILALOFS.NS",
    "MPHASIS.NS", "MUTHOOTFIN.NS", "NAM-INDIA.NS", "NATIONALUM.NS", "NAUKRI.NS", "NBCC.NS",
    "NESTLEIND.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS", "NYKAA.NS", "OBEROIRLTY.NS", "OFSS.NS",
    "OIL.NS", "ONGC.NS", "PAGEIND.NS", "PATANJALI.NS", "PAYTM.NS", "PERSISTENT.NS", "PETRONET.NS",
    "PFC.NS", "PGEL.NS", "PHOENIXLTD.NS", "PIDILITIND.NS", "PIIND.NS", "PNB.NS", "PNBHOUSING.NS",
    "POLICYBZR.NS", "POLYCAB.NS", "POWERGRID.NS", "POWERINDIA.NS", "PREMIERENE.NS", "PRESTIGE.NS",
    "RADICO.NS", "RBLBANK.NS", "RECLTD.NS", "RELIANCE.NS", "RVNL.NS", "SAGILITY.NS", "SAIL.NS",
    "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS",
    "SOLARINDS.NS", "SONACOMS.NS", "SRF.NS", "SUNPHARMA.NS", "SUPREMEIND.NS", "SUZLON.NS",
    "SWIGGY.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TIINDIA.NS", "TITAN.NS", "TMPV.NS", "TORNTPHARM.NS", "TRENT.NS", "TVSMOTOR.NS",
    "UJJIVANSFB.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", "UNITDSPR.NS", "UNOMINDA.NS", "UPL.NS",
    "VBL.NS", "VEDL.NS", "VMM.NS", "VOLTAS.NS", "WAAREEENER.NS", "WIPRO.NS", "YESBANK.NS",
    "ZYDUSLIFE.NS",
]

BAR_MINUTES = 15
REQUEST_PAUSE_SECONDS = 0.3  # pause between symbols to avoid rate limiting
BREAKOUT_LOOKBACK = 20       # bars used to define the support/resistance level
ATR_PERIOD = 14
RSI_PERIOD = 14
TREND_EMA_SPAN = 50          # trend filter on the 15m series (proxy for higher timeframe)
VOLUME_MULTIPLE = 1.5        # signal bar volume must beat its baseline by this factor
MIN_BREAK_ATR = 0.1          # close must clear the level by at least 0.1 ATR
CLOSE_LOCATION = 0.7         # CE: close in top 30% of bar range; PE: bottom 30%
SAME_TIME_SESSIONS = 5       # sessions used for the time-of-day volume baseline
MIN_SAME_TIME_SESSIONS = 3   # below this, fall back to the rolling average
MIN_BARS = BREAKOUT_LOOKBACK + 30


def calculate_rsi(series, period=RSI_PERIOD):
    """Wilder-smoothed RSI."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    # No losses at all in the window means RSI is 100 (not NaN)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    return rsi


def calculate_atr(df, period=ATR_PERIOD):
    prev_close = df['Close'].shift(1)
    true_range = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - prev_close).abs(),
        (df['Low'] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def drop_forming_bar(df):
    """yfinance returns the current, still-forming 15m bar. Drop it so signals use completed bars only."""
    if df.empty:
        return df
    now = pd.Timestamp.now(tz=df.index.tz) if df.index.tz is not None else pd.Timestamp.now()
    if now < df.index[-1] + pd.Timedelta(minutes=BAR_MINUTES):
        return df.iloc[:-1]
    return df


def volume_baseline(df, pos):
    """
    Expected volume for the bar at position `pos`. Uses the same time of day over
    previous sessions, because volume is heavy at the open and close. Falls back to
    the rolling average if there are not enough prior sessions.
    """
    bar_time = df.index[pos].time()
    bar_date = df.index[pos].date()
    same_time = df[(df.index.time == bar_time) & (df.index.date < bar_date)]['Volume']
    same_time = same_time.tail(SAME_TIME_SESSIONS)
    if len(same_time) >= MIN_SAME_TIME_SESSIONS:
        return float(same_time.mean())
    rolling = df['Volume'].iloc[max(0, pos - BREAKOUT_LOOKBACK):pos]
    return float(rolling.mean()) if len(rolling) else np.nan


def evaluate_symbol(df):
    """
    Returns (setup_type, price_change_pct, rsi, score) for the last completed bar,
    or None if there is no fresh, confirmed breakout.
    """
    df = drop_forming_bar(df)
    if len(df) < MIN_BARS:
        return None

    df = df.copy()
    df['RSI'] = calculate_rsi(df['Close'])
    df['ATR'] = calculate_atr(df)
    df['EMA'] = df['Close'].ewm(span=TREND_EMA_SPAN, adjust=False).mean()

    s = len(df) - 1          # signal bar (last completed)
    p = s - 1                # previous bar

    bar = df.iloc[s]
    prev = df.iloc[p]

    # Levels from the BREAKOUT_LOOKBACK bars before the signal bar
    res = df['High'].iloc[s - BREAKOUT_LOOKBACK:s].max()
    sup = df['Low'].iloc[s - BREAKOUT_LOOKBACK:s].min()
    # Same levels as they stood one bar earlier, to detect a stale (already-broken) level
    prev_res = df['High'].iloc[p - BREAKOUT_LOOKBACK:p].max()
    prev_sup = df['Low'].iloc[p - BREAKOUT_LOOKBACK:p].min()

    values = [bar['ATR'], bar['RSI'], bar['EMA'], bar['Volume']]
    if any(pd.isna(v) for v in values) or bar['ATR'] <= 0:
        return None

    bar_range = bar['High'] - bar['Low']
    if bar_range <= 0:
        return None
    close_loc = (bar['Close'] - bar['Low']) / bar_range

    baseline = volume_baseline(df, s)
    if pd.isna(baseline) or baseline <= 0:
        return None
    volume_ok = bar['Volume'] > VOLUME_MULTIPLE * baseline

    price_change = ((bar['Close'] - prev['Close']) / prev['Close']) * 100
    vol_ratio = bar['Volume'] / baseline

    # Bullish: fresh upside break, close near the high, uptrend, RSI and volume confirm
    is_ce = (
        bar['Close'] > res + MIN_BREAK_ATR * bar['ATR'] and
        prev['Close'] <= prev_res and              # first bar through the level, not a chase
        close_loc >= CLOSE_LOCATION and
        bar['Close'] > bar['EMA'] and
        bar['RSI'] > 50 and
        volume_ok
    )
    # Bearish: mirror image
    is_pe = (
        bar['Close'] < sup - MIN_BREAK_ATR * bar['ATR'] and
        prev['Close'] >= prev_sup and
        close_loc <= (1 - CLOSE_LOCATION) and
        bar['Close'] < bar['EMA'] and
        bar['RSI'] < 50 and
        volume_ok
    )

    if is_ce:
        strength = (bar['Close'] - res) / bar['ATR']
        setup_type = "CE (Bullish)"
    elif is_pe:
        strength = (sup - bar['Close']) / bar['ATR']
        setup_type = "PE (Bearish)"
    else:
        return None

    score = round(float(strength * vol_ratio), 2)
    return setup_type, round(float(price_change), 2), float(bar['RSI']), score


def scan_fno_market():
    results = []
    failed = []
    print(f"Scanning {len(FNO_SYMBOLS)} F&O stocks for confirmed breakout CE & PE setups...")

    for symbol in FNO_SYMBOLS:
        try:
            df = yf.Ticker(symbol).history(period="5d", interval="15m")
            if df.empty:
                failed.append(symbol)
                continue
            evaluated = evaluate_symbol(df)
            if evaluated is None:
                continue
            setup_type, price_change, rsi, score = evaluated
            last_close = float(drop_forming_bar(df)['Close'].iloc[-1])
            results.append({
                "symbol": symbol,
                "type": setup_type,
                "price": round(last_close, 2),
                "price_change_pct": price_change,
                "volume": int(drop_forming_bar(df)['Volume'].iloc[-1]),
                "rsi": round(rsi, 2),
                "score": score,
            })
        except Exception as e:
            failed.append(f"{symbol} ({e.__class__.__name__})")
            continue
        finally:
            time.sleep(REQUEST_PAUSE_SECONDS)

    if failed:
        print(f"No data for {len(failed)} symbols: {', '.join(failed)}")
    return pd.DataFrame(results)


if __name__ == "__main__":
    print(scan_fno_market().to_string(index=False))
