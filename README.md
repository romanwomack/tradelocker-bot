# TradeLocker EURUSD Bot (Railway-ready)

A session-gated, risk-first EURUSD bot for the **TradeLocker** _demo_ environment.

> **What it does**
> - Trades **EURUSD** only during **London (07:00–11:00 UK)** and **New York (08:00–11:00 NY)** sessions
> - Strategy: simple mechanical rules (EMA trend + BOS + pullback) and **ATR trailing stop**
> - **Risk caps**: max **0.1% daily loss**, target **+5% weekly** (pauses trading once hit)
> - Runs a FastAPI service (healthcheck `/`) for Railway
> - Webhook `/webhooks/fill` to record realized PnL if your TL demo can post fills

## Quick start

1. **Clone** and fill in `.env` based on `.env.example`.
2. Ensure your **TradeLocker demo base URL** and endpoints match the ones in `app/tradelocker_client.py`. Adjust paths as needed.
3. Run locally:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
