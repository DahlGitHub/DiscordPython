from datetime import datetime, timezone
from dateutil import tz
import parsedatetime as pdt
from dateutil.relativedelta import relativedelta

cal = pdt.Calendar(version=pdt.VERSION_CONTEXT_STYLE)
oslo_tz = tz.gettz("Europe/Oslo")

def parse_time_and_message(text: str):
    """Returns (when: datetime | None, message: str)."""
    now = datetime.now(oslo_tz)
    result = cal.nlp(text, sourceTime=now)
    if not result:
        return None, None

    dt, _status, start, end, _matched = result[0]


    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=oslo_tz)

    when_utc = dt.astimezone(timezone.utc)

    message = (text[:start] + text[end:]).strip(" ,.!-–—")
    if not message:
        message = "No message"

    return when_utc, message

def human_timedelta(dt: datetime, now: datetime = None, accuracy: int = 3) -> str:
    now = now or datetime.now(timezone.utc)
    delta = relativedelta(dt, now)

    parts = []
    if delta.years:
        parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")
    if delta.months:
        parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")
    if delta.days:
        parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")
    if delta.hours:
        parts.append(f"{delta.hours} hour{'s' if delta.hours != 1 else ''}")
    if delta.minutes:
        parts.append(f"{delta.minutes} minute{'s' if delta.minutes != 1 else ''}")

    return ', '.join(parts[:accuracy])