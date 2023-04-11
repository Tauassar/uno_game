from __future__ import annotations

import datetime
import typing
import zoneinfo


TIMEZONES = zoneinfo.available_timezones()
UTC = zoneinfo.ZoneInfo('UTC')


class Time:
    def __init__(self, units: int):
        # Units are milliseconds.
        self._units = units

    def _op(
        self, other: typing.Union[int, Time], operator: typing.Callable[[int], int],
    ) -> Time:
        if not isinstance(other, (int, Time)):
            return NotImplemented

        if isinstance(other, int):
            return self.__class__(operator(other))

        return self.__class__(operator(other._units))

    def __mul__(self, other: typing.Union[int, Time]) -> Time:
        return self._op(other, self._units.__mul__)

    def __rmul__(self, other: typing.Union[int, Time]) -> Time:
        return self._op(other, self._units.__mul__)

    def __sub__(self, other: typing.Union[int, Time]) -> Time:
        return self._op(other, self._units.__sub__)

    def __eq__(self, other: typing.Union[int, Time]) -> bool:
        if not isinstance(other, (int, Time)):
            return NotImplemented

        if isinstance(other, int):
            return self._units == other

        return self._units == other._units

    @property
    def seconds(self) -> int:
        return self._units // 1000

    @property
    def millis(self) -> int:
        return self._units


Millisecond = Time(1)
Second = 1000 * Millisecond
Minute = 60 * Second
Hour = 60 * Minute
Day = 24 * Hour
Month = 31 * Day


def dt_to_millis(dt: datetime.datetime) -> int:
    """Converts datetime object to milliseconds."""
    return int(dt.timestamp() * 1000)


def utcnow() -> datetime.datetime:
    """Return current datetime with UTC timezone."""
    return datetime.datetime.now(tz=UTC)


def ensure_dt_aware(dt: datetime.datetime, tz: zoneinfo.ZoneInfo = UTC) -> datetime.datetime:
    """Ensure passed datetime is in UTC

    If the datetime is aware, convert it to UTC.
    If it's naive, interpret it as UTC and make it aware.
    """

    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)

    return dt.astimezone(tz)


def round_ts_up_to_step(ts: typing.Union[int, Time], step: typing.Union[int, Time]) -> int:
    """Round up and step the timestamp."""

    if isinstance(ts, Time):
        ts = ts.millis
    if isinstance(step, Time):
        step = step.millis

    return ts // step * step + step


def ts_to_datetime(ts: int) -> datetime.datetime:
    """Convert timestamp to datetime object.

    Timestamp must be in milliseconds.
    """
    return ensure_dt_aware(datetime.datetime.utcfromtimestamp(ts / 1000))


def iso_to_datetime(iso: str) -> datetime.datetime:
    """Converts datetime string in iso format to datetime object."""
    return ensure_dt_aware(datetime.datetime.fromisoformat(iso))


def date_to_datetime(
    date: datetime.date, extra_timedelta: datetime.timedelta = None,
) -> datetime.datetime:
    """Convert date object to datetime object.

    Optionally add extra time delta to the result datetime object.
    """
    dt = datetime.datetime(year=date.year, month=date.month, day=date.day)

    if extra_timedelta is not None:
        dt += extra_timedelta

    return ensure_dt_aware(dt)


def is_expired(
    ts: int,
    ttl: int,
) -> bool:
    """Check if given ts plus ttl greater than or equals to current time."""
    event_dt = ts_to_datetime(ts)

    return event_dt + datetime.timedelta(days=ttl) < utcnow()


def timezone(tzname: str) -> zoneinfo.ZoneInfo:
    """Convert time zone name to concrete ZoneInfo."""
    try:
        return zoneinfo.ZoneInfo(tzname)
    except zoneinfo.ZoneInfoNotFoundError as e:
        raise ValueError(f'no time zone found: {tzname!r}') from e


def seconds_from_time(
    time: typing.Optional[typing.Union[Time, int]],
) -> typing.Union[None, int]:
    """Extract seconds from ``Time`` object.

    If ``int`` value is passed, return it as is.
    """
    if time is None:
        return None

    if isinstance(time, int):
        return time

    return time.seconds
