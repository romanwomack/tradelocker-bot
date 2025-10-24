import requests
from typing import Dict, List, Optional
from datetime import datetime
from app.config import settings

class TradeLockerClient:
    def __init__(self, api_key: str = None, base_url: str = None, account_id: str = None, timeout: int = None):
        self.api_key = api_key or settings.TL_API_KEY
        self.base_url = (base_url or settings.TL_BASE_URL).rstrip("/")
        self.account_id = account_id or settings.TL_ACCOUNT_ID
        self.timeout = timeout or settings.TL_TIMEOUT

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    # ---- Account ----
    def get_account_equity(self) -> float:
        # Placeholder endpoint – adjust to actual TradeLocker demo API path
        r = requests.get(f"{self.base_url}/accounts/{self.account_id}", headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return float(data.get("equity", 0.0))

    # ---- Market Data ----
    def get_candles(self, symbol: str, timeframe: str, limit: int = 300) -> List[Dict]:
        # Placeholder endpoint – adjust to actual TradeLocker demo API path
        params = {"symbol": symbol, "timeframe": timeframe, "limit": limit}
        r = requests.get(f"{self.base_url}/marketdata/candles", headers=self._headers(), params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["candles"]  # each: {ts, open, high, low, close, volume}

    # ---- Orders/Positions ----
    def place_order(self, symbol: str, side: str, qty: float, entry_type: str, price: Optional[float], sl: Optional[float], tp: Optional[float]) -> Dict:
        payload = {
            "accountId": self.account_id,
            "symbol": symbol,
            "side": side,                # "BUY" / "SELL"
            "type": entry_type,          # "MARKET" / "LIMIT"
            "price": price,
            "stopLoss": sl,
            "takeProfit": tp,
            "quantity": qty
        }
        r = requests.post(f"{self.base_url}/orders", json=payload, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def modify_order(self, order_id: str, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict:
        payload = {"stopLoss": sl, "takeProfit": tp}
        r = requests.patch(f"{self.base_url}/orders/{order_id}", json=payload, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_open_positions(self) -> List[Dict]:
        r = requests.get(f"{self.base_url}/accounts/{self.account_id}/positions", headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json().get("positions", [])

    def close_position(self, position_id: str) -> Dict:
        r = requests.post(f"{self.base_url}/positions/{position_id}/close", headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()
