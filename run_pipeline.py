import sys
import os
import pandas as pd
from importlib.machinery import SourceFileLoader

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

scan_mod = SourceFileLoader("scan", "trader-scanner/scan.py").load_module()
broker_mod = SourceFileLoader("ticket", "trader-broker/ticket.py").load_module()
size_mod = SourceFileLoader("size", "trader-budget/size.py").load_module()
risk_mod = SourceFileLoader("check", "trader-risk/check.py").load_module()
exit_mod = SourceFileLoader("exit", "trader-exit/exit.py").load_module()

scan_fno_market = scan_mod.scan_fno_market
IndianBrokerClient = broker_mod.IndianBrokerClient
calculate_fno_position_size = size_mod.calculate_fno_position_size
check_fno_risk_limits = risk_mod.check_fno_risk_limits
calculate_exit_targets = exit_mod.calculate_exit_targets

def run_fno_trading_pipeline():
    print("=" * 70)
    print("🚀 RUNNING PIPELINE: GUARANTEED TOP 2 CE & TOP 2 PE SETUPS")
    print("=" * 70)

    df_scan = scan_fno_market()
    if df_scan.empty:
        print(" -> No stocks met market filters today.")
        return

    processed_setups = []

    for _, row in df_scan.iterrows():
        symbol = row['symbol']
        price = row['price']
        setup_type = row['type']
        is_long = ("CE" in setup_type)

        risk_check = check_fno_risk_limits(500000.0, 1000.0, 15000.0, 100000.0)
        if not risk_check["approved"]:
            continue

        sl_price = price * 0.98 if is_long else price * 1.02
        lots, qty = calculate_fno_position_size(500000.0, 1.5, price, sl_price, lot_size=25)
        if lots == 0:
            continue

        targets = calculate_exit_targets(entry_price=price, is_long=is_long, atr=price * 0.015)

        processed_setups.append({
            "Symbol": symbol,
            "Type": setup_type,
            "LTP (₹)": price,
            "RSI": row['rsi'],
            "Score": row['score'],
            "Approved Lots": lots,
            "Total Qty": qty,
            "Target (₹)": targets["target"],
            "Stop Loss (₹)": targets["stop_loss"]
        })

    if not processed_setups:
        print("No setups passed the sizing & risk framework.")
        return

    df_results = pd.DataFrame(processed_setups)

    # Separate and rank CE and PE independently
    ce_setups = df_results[df_results["Type"].str.contains("CE")].sort_values(by="Score", ascending=False)
    pe_setups = df_results[df_results["Type"].str.contains("PE")].sort_values(by="Score", ascending=False)

    top_2_ce = ce_setups.head(2)
    top_2_pe = pe_setups.head(2)

    # Fallback if PE count is less than 2: pull lowest RSI stocks from scan to fill the 2 PE slots
    if len(top_2_pe) < 2:
        remaining_needed = 2 - len(top_2_pe)
        df_fallback_pe = df_results[~df_results["Symbol"].isin(top_2_pe["Symbol"])].sort_values(by="RSI", ascending=True).head(remaining_needed)
        df_fallback_pe["Type"] = "PE (Bearish - Fallback)"
        top_2_pe = pd.concat([top_2_pe, df_fallback_pe])

    final_top_4 = pd.concat([top_2_ce, top_2_pe]).reset_index(drop=True)

    print("\n" + "=" * 70)
    print("🏆 BALANCED FINAL SELECTION: TOP 2 CE & TOP 2 PE SETUPS")
    print("=" * 70)
    print(final_top_4[['Symbol', 'Type', 'LTP (₹)', 'RSI', 'Score', 'Approved Lots', 'Total Qty', 'Target (₹)', 'Stop Loss (₹)']].to_string(index=False))

if __name__ == "__main__":
    run_fno_trading_pipeline()