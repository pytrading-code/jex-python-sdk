from datetime import datetime, timedelta

def interval_to_seconds(interval):
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60,
    }
    try:
        return int(interval[:-1]) * seconds_per_unit[interval[-1]]
    except (ValueError, KeyError):
        return None

def strtime_to_datetime(strtime):
    return datetime.strptime(strtime, "%Y-%m-%d %H:%M:%S") 

def datetime_to_strtime(dtime):
    return dtime.strftime("%Y-%m-%d %H:%M:%S")

def datetime_to_timestamp(dtime):
    return int(datetime.timestamp(dtime)*1e3)

def timestamp_to_datetime(ts):
    return datetime.fromtimestamp(ts/1e3)

def strtime_to_timestamp(strtime):
    return datetime_to_timestamp(strtime_to_datetime(strtime))

def timestamp_to_strtime(ts):
    return datetime_to_strtime(timestamp_to_datetime(ts))
