from typing import List, Dict
from datetime import datetime, timedelta, timezone
import math

# This module expects the TradeLocker client to provide candle data.
# Candles = dict(ts, open, high, low, close, volume)

def ema(series: List[float], length: int) -> List[float]:
    if length <= 1: return series[:]
    k = 2 / (length + 1)
    out = []
    prev = None
    for v in series:
        prev = v if prev is None else (v - prev) * k + prev
        out.append(prev)
    return out

def atr(candles: List[Dict], length: int) -> float:
    trs = []
    prev_close = None
    for c in candles:
        h, l, cl = c["high"], c["low"], c["close"]
        if prev_close is None:
            tr = h - l
        else:
            tr = max(h - l, abs(h - prev_close), abs(l - prev_close))
        trs.append(tr)
        prev_close = cl
    if len(trs) < length: return sum(trs)/max(1,len(trs))
    # simple SMA ATR (fine for runtime)
    return sum(trs[-length:]) / length

def find_swings(candles: List[Dict], lookback=5):
    # very simple swing detection: highest/lowest of last N
    closes = [c["close"] for c in candles]
    highs  = [c["high"]  for c in candles]
    lows   = [c["low"]   for c in candles]
    swing_high = max(highs[-lookback-1:-1]) if len(highs) > lookback else highs[-1]
    swing_low  = min(lows[-lookback-1:-1]) if len(lows) > lookback else lows[-1]
    return swing_high, swing_low
 
