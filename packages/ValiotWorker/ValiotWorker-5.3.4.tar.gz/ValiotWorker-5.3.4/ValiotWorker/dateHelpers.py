from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone


def getUtcDate(date: datetime) -> datetime:
    utc = timezone('UTC')
    utc_date = date.astimezone(utc)
    return utc_date
