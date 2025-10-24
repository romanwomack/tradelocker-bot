import os
from dataclasses import dataclass

@dataclass
class Settings:
    # Core
    ENV: str = os.getenv("ENV", "production")
    SYMBOL: str = os.getenv("SYMBOL", "EURUSD")

    # TradeLocker
    TL_BASE_URL: str = os.getenv("TL_BASE_URL", "https://demo.tradelocker.example/api")  # <-- set your real demo base URL
    TL_API_KEY: str = os.getenv("TL_API_KEY", "")
    TL_ACCOUNT_ID: str = os.getenv("TL_ACCOUNT_ID", "")
    TL_TIMEOUT: int = int(os.getenv("TL_TIMEOUT", "15"))

    # Trading windows (IANA tz)
    LONDON_TZ: str = os.getenv("LONDON_TZ", "Europe/London")
    NEWYORK_TZ: str = os.getenv("NEWYORK_TZ", "America/New_York")
    # Session windows (local exchange/session times)
    LONDON_START: str = os.getenv("LONDON_START", "07:00")   # 07:00–11:00 London
    LONDON_END: str   = os.getenv("LONDON_END", "11:00")
    NY_START: str     = os.getenv("NY_START", "08:00")       # 08:00–11:00 New York
    NY_END: str       = os.getenv("NY_END", "11:00")

    # Risk & goals
    MAX_DAILY_LOSS_FRAC: float = float(os.getenv("MAX_DAILY_LOSS_FRAC", "0.001"))  # 0.1%
    WEEKLY_TARGET_FRAC: float = float(os.getenv("WEEKLY_TARGET_FRAC", "0.05"))     # 5%
    BASE_RISK_PER_TRADE_FRAC: float = float(os.getenv("BASE_RISK_PER_TRADE_FRAC", "0.0003"))  # 0.03%/trade baseline
    MAX_CONCURRENT_POSITIONS: int = int(os.getenv("MAX_CONCURRENT_POSITIONS", "1"))

    # Strategy params
    TIMEFRAME: str = os.getenv("TIMEFRAME", "M5")
    EMA_FAST: int = int(os.getenv("EMA_FAST", "20"))
    EMA_SLOW: int = int(os.getenv("EMA_SLOW", "50"))
    ATR_LEN: int = int(os.getenv("ATR_LEN", "14"))
    ATR_TS_MULT: float = float(os.getenv("ATR_TS_MULT", "2.0"))   # trailing stop multiplier
    TAKE_PROFIT_R_MULT: float = float(os.getenv("TAKE_PROFIT_R_MULT", "1.5"))

    # Server
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
