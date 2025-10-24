from fastapi import FastAPI, Request
from app.config import settings
from app.scheduler import start_scheduler, get_engine

app = FastAPI(title="TradeLocker EURUSD Bot")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def root():
    return {"service": "tradelocker-eurusd-bot", "symbol": settings.SYMBOL}

@app.post("/webhooks/fill")
async def webhook_fill(req: Request):
    payload = await req.json()
    eng = get_engine()
    eng.on_fill_webhook(payload)
    return {"ok": True}
 
