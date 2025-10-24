from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.trading_engine import Engine

_engine = Engine()

def start_scheduler():
    sched = BackgroundScheduler(timezone="UTC")
    # run every minute on M5 strategy; you can also align to candle boundaries
    sched.add_job(_engine.tick, IntervalTrigger(minutes=1), id="minute-tick", max_instances=1, replace_existing=True)
    sched.start()
    return sched

def get_engine():
    return _engine
 
