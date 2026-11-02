def calculate_exit_targets(entry_price: float, is_long: bool, atr: float):
    if is_long:
        target = entry_price + (2.5 * atr)
        stop_loss = entry_price - (1.5 * atr)
    else:
        target = entry_price - (2.5 * atr)
        stop_loss = entry_price + (1.5 * atr)
    return {"target": round(target, 2), "stop_loss": round(stop_loss, 2)}

if __name__ == "__main__":
    print(calculate_exit_targets(2450.0, True, 22.5))
