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

    def build_setup(row, is_long, setup_type):
        symbol = row['symbol']
        price = row['price']

        risk_check = check_fno_risk_limits(500000.0, 1000.0, 15000.0, 100000.0)
        if not risk_check["approved"]:
            return None

        sl_price = price * 0.98 if is_long else price * 1.02
        lots, qty = calculate_fno_position_size(500000.0, 1.5, price, sl_price, lot_size=25)
        if lots == 0:
            return None

        targets = calculate_exit_targets(entry_price=price, is_long=is_long, atr=price * 0.015)

        return {
            "Symbol": symbol,
            "Type": setup_type,
            "LTP (₹)": price,
            "RSI": row['rsi'],
            "Score": row['score'],
            "Approved Lots": lots,
            "Total Qty": qty,
            "Target (₹)": targets["target"],
            "Stop Loss (₹)": targets["stop_loss"]
        }

    processed_setups = []
    for _, row in df_scan.iterrows():
        is_long = ("CE" in row['type'])
        setup = build_setup(row, is_long, row['type'])
        if setup is not None:
            processed_setups.append(setup)

    if not processed_setups:
        print("No setups passed the sizing & risk framework.")
        return

    df_results = pd.DataFrame(processed_setups)

    # Separate and rank CE and PE independently
    ce_setups = df_results[df_results["Type"].str.contains("CE")].sort_values(by="Score", ascending=False)
    pe_setups = df_results[df_results["Type"].str.contains("PE")].sort_values(by="Score", ascending=False)

    top_2_ce = ce_setups.head(2)
    top_2_pe = pe_setups.head(2)

    # Fallback if PE count is less than 2: take the lowest-RSI stocks from the scan and
    # build them as genuine SHORT (bearish) setups, so target is below and stop is above entry.
    if len(top_2_pe) < 2:
        needed = 2 - len(top_2_pe)
        used = set(top_2_ce["Symbol"]) | set(top_2_pe["Symbol"])
        fallback_setups = []
        for _, row in df_scan.sort_values(by="rsi", ascending=True).iterrows():
            if len(fallback_setups) >= needed:
                break
            if row['symbol'] in used:
                continue
            setup = build_setup(row, False, "PE (Bearish - Fallback)")
            if setup is not None:
                fallback_setups.append(setup)
                used.add(row['symbol'])
        if fallback_setups:
            top_2_pe = pd.concat([top_2_pe, pd.DataFrame(fallback_setups)])

    final_top_4 = pd.concat([top_2_ce, top_2_pe]).reset_index(drop=True)

    print("\n" + "=" * 70)
    print("🏆 BALANCED FINAL SELECTION: TOP 2 CE & TOP 2 PE SETUPS")
    print("=" * 70)
    print(final_top_4[['Symbol', 'Type', 'LTP (₹)', 'RSI', 'Score', 'Approved Lots', 'Total Qty', 'Target (₹)', 'Stop Loss (₹)']].to_string(index=False))

if __name__ == "__main__":
    run_fno_trading_pipeline()