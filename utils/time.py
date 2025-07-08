from datetime import datetime
from dateutil import tz
import parsedatetime as pdt

cal = pdt.Calendar(version=pdt.VERSION_CONTEXT_STYLE)
oslo_tz = tz.gettz("Europe/Oslo")

def parse_time_and_message(input_str: str):
    now = datetime.now(oslo_tz)  # Use Oslo time as the base time
    result = cal.nlp(input_str, sourceTime=now)
    if not result:
        return None, None

    dt, status, start, end, matched = result[0]

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=oslo_tz)

    # Convert to UTC for storing / scheduling
    dt = dt.astimezone(tz.UTC)

    remaining = input_str[end:].strip(" ,.!") or "No message"
    return dt, remaining