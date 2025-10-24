from datetime import datetime, time
from zoneinfo import ZoneInfo

def in_session(now_utc: datetime, tz_name: str, start: str, end: str) -> bool:
    tz = ZoneInfo(tz_name)
    local = now_utc.astimezone(tz)
    s_hour, s_min = map(int, start.split(":"))
    e_hour, e_min = map(int, end.split(":"))
    start_t = time(s_hour, s_min)
    end_t = time(e_hour, e_min)
    return start_t <= local.time() <= end_t

def is_prime_session(now_utc: datetime, london_conf, ny_conf) -> bool:
    return (
        in_session(now_utc, london_conf["tz"], london_conf["start"], london_conf["end"]) or
        in_session(now_utc, ny_conf["tz"], ny_conf["start"], ny_conf["end"])
    )
