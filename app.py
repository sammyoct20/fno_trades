import streamlit as st
import pandas as pd
import sys
import os

# Set page layout
st.set_page_config(page_title="Indian F&O Top Setups", layout="wide")

st.title("🚀 Indian F&O Top 2 CE & PE Automated Scanner")
st.markdown("This dashboard scans the NSE F&O universe, applies multi-condition rules, and extracts the best trading setups.")

if st.button("🔍 Run Full Market Scan & Pipeline", type="primary"):
    with st.spinner("Scanning NSE/BSE F&O universe and calculating risk metrics..."):
        
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from importlib.machinery import SourceFileLoader
        
        try:
            scan_mod = SourceFileLoader("scan", "trader-scanner/scan.py").load_module()
            size_mod = SourceFileLoader("size", "trader-budget/size.py").load_module()
            exit_mod = SourceFileLoader("exit", "trader-exit/exit.py").load_module()
            
            df_scan = scan_mod.scan_fno_market()
            
            if df_scan.empty:
                st.warning("No stocks met the criteria on this scan.")
            else:
                processed_setups = []
                for _, row in df_scan.iterrows():
                    symbol = row['symbol']
                    price = row['price']
                    setup_type = row['type']
                    is_long = ("CE" in setup_type)

                    sl_price = price * 0.98 if is_long else price * 1.02
                    lots, qty = size_mod.calculate_fno_position_size(500000.0, 1.5, price, sl_price, lot_size=25)
                    if lots == 0:
                        continue

                    targets = exit_mod.calculate_exit_targets(entry_price=price, is_long=is_long, atr=price * 0.015)

                    processed_setups.append({
                        "Symbol": symbol,
                        "Type": setup_type,
                        "LTP (₹)": price,
                        "Change %": row['price_change_pct'],
                        "RSI": row['rsi'],
                        "Score": row['score'],
                        "Approved Lots": lots,
                        "Total Qty": qty,
                        "Target (₹)": targets["target"],
                        "Stop Loss (₹)": targets["stop_loss"]
                    })

                if not processed_setups:
                    st.warning("Scanned stocks failed risk/sizing guardrails.")
                else:
                    df_results = pd.DataFrame(processed_setups)

                    # Separate CE and PE
                    ce_setups = df_results[df_results["Type"].str.contains("CE")].sort_values(by="Score", ascending=False).head(2)
                    pe_setups = df_results[df_results["Type"].str.contains("PE")].sort_values(by="Score", ascending=False).head(2)

                    # Guaranteed Fallback: If no PE setups found, take the weakest/lowest RSI stocks from scan as PE candidates
                    # Fallback PE: build genuine SHORT setups from the lowest-RSI scan rows
                    # (target below entry, stop above entry), not relabelled CE trades.
                    def build_fallback_short(row):
                        price = row['price']
                        sl_price = price * 1.02
                        lots, qty = size_mod.calculate_fno_position_size(500000.0, 1.5, price, sl_price, lot_size=25)
                        if lots == 0:
                            return None
                        targets = exit_mod.calculate_exit_targets(entry_price=price, is_long=False, atr=price * 0.015)
                        return {
                            "Symbol": row['symbol'],
                            "Type": "PE (Bearish - Weakness)",
                            "LTP (₹)": price,
                            "Change %": row['price_change_pct'],
                            "RSI": row['rsi'],
                            "Score": row['score'],
                            "Approved Lots": lots,
                            "Total Qty": qty,
                            "Target (₹)": targets["target"],
                            "Stop Loss (₹)": targets["stop_loss"]
                        }

                    if len(pe_setups) < 2:
                        needed = 2 - len(pe_setups)
                        used = set(ce_setups["Symbol"]) | set(pe_setups["Symbol"])
                        fallback_setups = []
                        for _, row in df_scan.sort_values(by="rsi", ascending=True).iterrows():
                            if len(fallback_setups) >= needed:
                                break
                            if row['symbol'] in used:
                                continue
                            setup = build_fallback_short(row)
                            if setup is not None:
                                fallback_setups.append(setup)
                                used.add(row['symbol'])
                        if fallback_setups:
                            pe_setups = pd.concat([pe_setups, pd.DataFrame(fallback_setups)])

                    st.success("Scan Complete!")

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🟢 Top 2 CE (Bullish) Setups")
                        if not ce_setups.empty:
                            st.dataframe(ce_setups[['Symbol', 'LTP (₹)', 'Change %', 'RSI', 'Approved Lots', 'Target (₹)', 'Stop Loss (₹)']], use_container_width=True)
                        else:
                            st.info("No active CE setups found.")

                    with col2:
                        st.subheader("🔴 Top 2 PE (Bearish) Setups")
                        if not pe_setups.empty:
                            st.dataframe(pe_setups[['Symbol', 'LTP (₹)', 'Change %', 'RSI', 'Approved Lots', 'Target (₹)', 'Stop Loss (₹)']], use_container_width=True)
                        else:
                            st.info("No active PE setups found.")

        except Exception as e:
            st.error(f"Error running pipeline: {e}")
