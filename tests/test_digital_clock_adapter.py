from datetime import datetime

import pytest

from adapters import DigitalClockAdapter
from client.digital_clock_display import DigitalClockDisplay
from clocks import AnalogClock
from consts import DayNightDivision


@pytest.mark.parametrize(
    ("value", "hour_angle", "minute_angle", "second_angle", "division"),
    [
        (datetime(2026, 9, 24, 15, 30, 45), 90.0, 180.0, 270.0, DayNightDivision.PM),
        (datetime(2026, 9, 24, 0, 0, 0), 0.0, 0.0, 0.0, DayNightDivision.AM),
        (datetime(2026, 9, 24, 12, 0, 0), 0.0, 0.0, 0.0, DayNightDivision.PM),
        (datetime(2026, 9, 24, 11, 59, 59), 330.0, 354.0, 354.0, DayNightDivision.AM),
        (datetime(2026, 9, 24, 23, 59, 59), 330.0, 354.0, 354.0, DayNightDivision.PM),
    ],
)
def test_set_date_time_maps_time_to_dial_angles(
    value: datetime,
    hour_angle: float,
    minute_angle: float,
    second_angle: float,
    division: DayNightDivision,
) -> None:
    clock = AnalogClock()
    adapter = DigitalClockAdapter(clock)

    adapter.set_date_time(value)

    assert clock.get_hour_angle() == hour_angle
    assert clock.get_minute_angle() == minute_angle
    assert clock.get_second_angle() == second_angle
    assert clock.get_day_night_division() is division
    assert clock.get_year() == value.year
    assert clock.get_month() == value.month
    assert clock.get_day() == value.day


def test_set_date_time_rounds_microseconds_to_nearest_second() -> None:
    clock = AnalogClock()
    adapter = DigitalClockAdapter(clock)

    adapter.set_date_time(datetime(2026, 9, 24, 12, 0, 0, 700_000))

    assert clock.get_hour_angle() == 0.0
    assert clock.get_minute_angle() == 0.0
    assert clock.get_second_angle() == 6.0
    assert clock.get_day_night_division() is DayNightDivision.PM


def test_set_date_time_carries_rounded_second_into_minute() -> None:
    clock = AnalogClock()
    adapter = DigitalClockAdapter(clock)

    adapter.set_date_time(datetime(2026, 9, 24, 12, 0, 59, 700_000))

    assert clock.get_hour_angle() == 0.0
    assert clock.get_minute_angle() == 6.0
    assert clock.get_second_angle() == 0.0
    assert clock.get_day_night_division() is DayNightDivision.PM


@pytest.mark.parametrize(
    ("hour_angle", "minute_angle", "second_angle", "division", "expected"),
    [
        (90.0, 180.0, 270.0, DayNightDivision.AM, datetime(2026, 9, 24, 3, 30, 45)),
        (0.0, 0.0, 0.0, DayNightDivision.AM, datetime(2026, 9, 24, 0, 0, 0)),
        (0.0, 0.0, 0.0, DayNightDivision.PM, datetime(2026, 9, 24, 12, 0, 0)),
        (330.0, 354.0, 354.0, DayNightDivision.AM, datetime(2026, 9, 24, 11, 59, 59)),
        (330.0, 354.0, 354.0, DayNightDivision.PM, datetime(2026, 9, 24, 23, 59, 59)),
    ],
)
def test_get_date_time_reads_dial_angles_as_time(
    hour_angle: float,
    minute_angle: float,
    second_angle: float,
    division: DayNightDivision,
    expected: datetime,
) -> None:
    clock = AnalogClock()
    clock.set_date_time(2026, 9, 24, hour_angle, minute_angle, second_angle, division)
    adapter = DigitalClockAdapter(clock)

    assert adapter.get_date_time() == expected


def test_set_then_get_returns_same_moment() -> None:
    adapter = DigitalClockAdapter(AnalogClock())
    value = datetime(2026, 9, 24, 12, 34, 56)

    adapter.set_date_time(value)

    assert adapter.get_date_time() == value


def test_display_renders_time_from_adapter() -> None:
    adapter = DigitalClockAdapter(AnalogClock())
    display = DigitalClockDisplay(adapter)

    adapter.set_date_time(datetime(2026, 9, 24, 15, 30, 45))

    assert display.render() == "2026-09-24 15:30:45"
