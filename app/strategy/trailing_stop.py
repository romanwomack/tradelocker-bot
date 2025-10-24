def calc_trailing_stop(entry_price: float, direction: str, atr_value: float, mult: float, current_price: float):
    # Classic ATR-based trailing stop
    offset = atr_value * mult
    if direction == "LONG":
        base = current_price - offset
        return max(base, entry_price - offset)  # never below initial protective SL by ATR
    else:
        base = current_price + offset
        return min(base, entry_price + offset)
 
