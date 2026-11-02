def check_fno_risk_limits(account_balance: float, current_drawdown: float, max_allowed_drawdown: float, required_margin: float):
    if current_drawdown >= max_allowed_drawdown:
        return {"approved": False, "reason": "Max daily drawdown limit breached. Trading halted."}
    if required_margin > account_balance:
        return {"approved": False, "reason": "Insufficient margin for F&O position (SPAN + Exposure)."}
    return {"approved": True, "reason": "Risk checks passed successfully."}

if __name__ == "__main__":
    print(check_fno_risk_limits(500000, 5000, 15000, 120000))
