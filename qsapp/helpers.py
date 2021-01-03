from datetime import datetime, timedelta
import logging.config

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module helpers.py loaded")


class Dates:
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    this_monday = now - timedelta(days=now.weekday())
    this_sunday = this_monday + timedelta(days=6)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = this_monday - timedelta(days=1)

    this_month_first = now.replace(day=1)
    this_month_last = (this_month_first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_month_last = this_month_first - timedelta(days=1)
    last_month_first = last_month_last.replace(day=1)

    last_90_days = now - timedelta(days=89)
    last_30_days = now - timedelta(days=29)
    last_7_days = now - timedelta(days=6)

    def count_previous_period(startdate, enddate):
        if len(startdate) > 10:
            start = datetime.strptime(startdate, "%Y-%m-%dT%H:%M:%S")
        else:
            start = datetime.strptime(startdate, "%Y-%m-%d")
        if len(enddate) > 10:
            end = datetime.strptime(enddate, "%Y-%m-%dT%H:%M:%S")
        else:
            end = datetime.strptime(enddate, "%Y-%m-%d")
        count_days = end - start
        previous_period_end = datetime.strftime(start - timedelta(days=1), "%Y-%m-%d")
        previous_period_start = datetime.strftime(start - timedelta(days=(count_days.days+1)), "%Y-%m-%d")
        return previous_period_start, previous_period_end
