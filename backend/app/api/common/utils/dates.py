from datetime import date, datetime


def today_string() -> str:
    return date.today().isoformat()


def now_string() -> str:
    return datetime.now().isoformat()
