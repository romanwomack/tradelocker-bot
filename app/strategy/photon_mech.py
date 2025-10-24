from typing import Optional, Dict, List
from app.data.marketdata import ema, atr, find_swings

"""
A minimalist, mechanical, session-gated strategy:
- Bias: EMA20 > EMA50 => long bias; EMA20 < EMA50 => short bias
- Structure trigger: candle close breaks prior swing high/low (BOS)
- Entry: pullback toward EMA20 after BOS in bias direction
- SL: beyond recent swing low/high
- TP: TAKE_PROFIT_R_MULT * R
- Trailing stop: ATR * ATR_TS_MULT
"""

def generate_signal(candles: List[Dict], ema_fast: int, ema_slow: int) -> Optional[Dict]:
    if len(candles) < max(ema_fast, ema_slow) + 10:
        return None
    closes = [c["close"] for c in candles]
    highs  = [c["high"] for c in candles]
    lows   = [c["low"] for c in candles]

    e_fast = ema(closes, ema_fast)
    e_slow = ema(closes, ema_slow)

    bias = "LONG" if e_fast[-1] > e_slow[-1] else "SHORT"
    swing_high, swing_low = find_swings(candles, lookback=10)
    last_close = closes[-1]
    prev_close = closes[-2]

    bos_long = prev_close <= swing_high and last_close > swing_high
    bos_short = prev_close >= swing_low and last_close < swing_low

    if bias == "LONG" and bos_long:
        # wait for pullback near EMA fast
        if abs(last_close - e_fast[-1]) / last_close <= 0.0003:  # ~3 pips tolerance on EURUSD
            entry = last_close
            sl = min(lows[-10:])  # protective stop under recent swing
            if entry - sl <= 0: return None
            return {"direction":"LONG","entry":entry,"sl":sl}
    if bias == "SHORT" and bos_short:
        if abs(last_close - e_fast[-1]) / last_close <= 0.0003:
            entry = last_close
            sl = max(highs[-10:])  # protective stop above recent swing
            if sl - entry <= 0: return None
            return {"direction":"SHORT","entry":entry,"sl":sl}

    return None

def compute_trade_levels(candles: List[Dict], signal: Dict, atr_len: int, tp_r_mult: float):
    _atr = atr(candles, atr_len)
    risk_per_unit = abs(signal["entry"] - signal["sl"])
    tp = signal["entry"] + tp_r_mult * risk_per_unit if signal["direction"] == "LONG" else signal["entry"] - tp_r_mult * risk_per_unit
    return {"atr": _atr, "tp": tp}
 
