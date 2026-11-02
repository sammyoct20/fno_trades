def calculate_fno_position_size(capital: float, risk_pct: float, entry_price: float, stop_loss: float, lot_size: int):
    risk_amount = capital * (risk_pct / 100.0)
    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share <= 0 or lot_size <= 0:
        return 0, 0
    allowed_lots = int((risk_amount / (risk_per_share * lot_size)))
    final_lots = max(0, allowed_lots)
    return final_lots, final_lots * lot_size

if __name__ == "__main__":
    lots, qty = calculate_fno_position_size(300000, 1.5, 24000, 23900, 25)
    print(f"Allocated Lots: {lots} | Total Quantity: {qty}")
