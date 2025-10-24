import sqlite3
from pathlib import Path
from datetime import date, datetime

DB_PATH = Path("/mnt/data/tradelocker_bot.sqlite")  # works locally and on Railway ephemeral fs

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS metrics(
        d TEXT PRIMARY KEY,
        week TEXT,
        equity_start REAL,
        realized_pnl REAL DEFAULT 0.0,
        weekly_equity_start REAL
    );""")
    return con

def ensure_today_row(today: date, week_key: str, equity_now: float):
    con = _conn()
    with con:
        cur = con.execute("SELECT d FROM metrics WHERE d=?", (today.isoformat(),))
        if cur.fetchone() is None:
            # find week start record
            cur2 = con.execute("SELECT weekly_equity_start FROM metrics WHERE week=? ORDER BY d ASC LIMIT 1", (week_key,))
            row = cur2.fetchone()
            weekly_equity_start = row[0] if row and row[0] is not None else equity_now
            con.execute("INSERT INTO metrics(d, week, equity_start, realized_pnl, weekly_equity_start) VALUES(?,?,?,?,?)",
                        (today.isoformat(), week_key, equity_now, 0.0, weekly_equity_start))
    con.close()

def add_realized_pnl(today: date, pnl: float):
    con = _conn()
    with con:
        con.execute("UPDATE metrics SET realized_pnl = COALESCE(realized_pnl,0)+? WHERE d=?", (pnl, today.isoformat()))
    con.close()

def get_today(today: date):
    con = _conn()
    cur = con.execute("SELECT equity_start, realized_pnl, weekly_equity_start, week FROM metrics WHERE d=?", (today.isoformat(),))
    row = cur.fetchone()
    con.close()
    if not row: return None
    return {"equity_start": row[0], "realized_pnl": row[1], "weekly_equity_start": row[2], "week": row[3]}
