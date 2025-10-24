from dataclasses import dataclass
from datetime import date
from app.storage import get_today, add_realized_pnl

@dataclass
class RiskState:
    can_trade: bool
    reason: str
    risk_per_trade: float  # fraction of equity

def check_risk(today: date, equity_now: float, max_daily_loss_frac: float, weekly_target_frac: float, base_risk_frac: float) -> RiskState:
    row = get_today(today)
    if not row:
        return RiskState(True, "init-day", base_risk_frac)
    day_start = row["equity_start"]
    daily_pnl = row["realized_pnl"]
    week_start = row["weekly_equity_start"]
    # daily loss cap
    if (day_start + daily_pnl) <= day_start * (1 - max_daily_loss_frac):
        return RiskState(False, "daily-loss-cap-reached", 0.0)
    # weekly target reached -> reduce risk to a token amount (or stop)
    if (equity_now) >= week_start * (1 + weekly_target_frac):
        return RiskState(False, "weekly-target-hit", 0.0)
    return RiskState(True, "ok", base_risk_frac)

def record_fill_pnl(today: date, realized_pnl: float):
    add_realized_pnl(today, realized_pnl)
