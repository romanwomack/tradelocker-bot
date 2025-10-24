from datetime import datetime, date, timezone
from typing import Optional
from app.config import settings
from app.tradelocker_client import TradeLockerClient
from app.utils.timezones import is_prime_session
from app.strategy.risk import check_risk, record_fill_pnl
from app.strategy.trailing_stop import calc_trailing_stop
from app.strategy.photon_mech import generate_signal, compute_trade_levels
from app.storage import ensure_today_row

SYMBOL = settings.SYMBOL

class Engine:
    def __init__(self):
        self.tl = TradeLockerClient()

    def tick(self):
        now_utc = datetime.now(timezone.utc)
        # Ensure daily/weekly rows exist
        equity = self.tl.get_account_equity()
        week_key = f"{now_utc.isocalendar().year}-W{now_utc.isocalendar().week}"
        ensure_today_row(date.today(), week_key, equity)

        # Session gating
        if not is_prime_session(
            now_utc,
            {"tz": settings.LONDON_TZ, "start": settings.LONDON_START, "end": settings.LONDON_END},
            {"tz": settings.NEWYORK_TZ, "start": settings.NY_START, "end": settings.NY_END}
        ):
            return {"status":"idle","reason":"outside-session"}

        risk_state = check_risk(date.today(), equity, settings.MAX_DAILY_LOSS_FRAC, settings.WEEKLY_TARGET_FRAC, settings.BASE_RISK_PER_TRADE_FRAC)
        if not risk_state.can_trade:
            return {"status":"paused","reason":risk_state.reason}

        # Pull candles
        candles = self.tl.get_candles(SYMBOL, settings.TIMEFRAME, limit=350)
        if len(candles) < 60:
            return {"status":"idle","reason":"insufficient-candles"}

        # Existing positions?
        positions = [p for p in self.tl.get_open_positions() if p.get("symbol")==SYMBOL]
        if positions:
            # Manage trailing stops
            pos = positions[0]
            direction = "LONG" if pos["side"] == "BUY" else "SHORT"
            last = candles[-1]["close"]
            from app.data.marketdata import atr
            _atr = atr(candles, settings.ATR_LEN)
            new_sl = calc_trailing_stop(entry_price=float(pos["avgPrice"]), direction=direction, atr_value=_atr,
                                        mult=settings.ATR_TS_MULT, current_price=last)
            # Only move SL in the favorable direction
            current_sl = float(pos.get("stopLoss") or 0.0)
            if direction == "LONG" and (current_sl == 0.0 or new_sl > current_sl):
                self.tl.modify_order(pos["orderId"], sl=new_sl, tp=None)
            elif direction == "SHORT" and (current_sl == 0.0 or new_sl < current_sl):
                self.tl.modify_order(pos["orderId"], sl=new_sl, tp=None)
            return {"status":"managing","new_sl":new_sl}

        # No position: look for fresh signal
        signal = generate_signal(candles, settings.EMA_FAST, settings.EMA_SLOW)
        if not signal:
            return {"status":"idle","reason":"no-signal"}

        levels = compute_trade_levels(candles, signal, settings.ATR_LEN, settings.TAKE_PROFIT_R_MULT)

        # Position sizing — risk fraction of equity
        risk_amt = equity * risk_state.risk_per_trade
        stop_dist = abs(signal["entry"] - signal["sl"])
        if stop_dist <= 0:
            return {"status":"idle","reason":"invalid-stop"}
        # EURUSD lot calc simplified: assume quantity is in lots where 1.0 ~ 100k; adapt to your TL contract spec
        # Value per pip and price scaling differ across brokers—double-check with your TL demo!
        qty = max(0.01, round(risk_amt / stop_dist, 2))  # naive; replace with broker's contract calc

        side = "BUY" if signal["direction"]=="LONG" else "SELL"
        order = self.tl.place_order(
            symbol=SYMBOL,
            side=side,
            qty=qty,
            entry_type="MARKET",
            price=None,
            sl=signal["sl"],
            tp=levels["tp"]
        )
        return {"status":"entered","order":order}

    def on_fill_webhook(self, payload: dict):
        """
        Call this from a broker/tradelocker webhook (if available) to record realized PnL.
        Payload should include realized PnL for the day; if not available,
        you can poll closed trades and diff them here.
        """
        realized = float(payload.get("realizedPnl", 0.0))
        if realized != 0.0:
            record_fill_pnl(date.today(), realized)
 
