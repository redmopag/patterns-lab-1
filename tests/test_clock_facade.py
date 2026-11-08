from datetime import datetime

import pytest

from adapters import DigitalClockAdapter
from clocks import AnalogClock
from facades import ClockFacade
from services import ClockFormatter, ClockHistory


def make_facade() -> ClockFacade:
    return ClockFacade(
        adapter=DigitalClockAdapter(AnalogClock()),
        formatter=ClockFormatter(),
        history=ClockHistory(),
    )


def test_set_then_get_returns_same_moment() -> None:
    facade = make_facade()
    value = datetime(2026, 9, 24, 15, 30, 45)

    facade.set_date_time(value)

    assert facade.get_date_time() == value


def test_get_formatted_uses_default_format() -> None:
    facade = make_facade()
    facade.set_date_time(datetime(2026, 9, 24, 12, 34, 56))

    assert facade.get_formatted() == "24.09.2026 12:34:56"


def test_get_formatted_respects_custom_format() -> None:
    facade = make_facade()
    facade.set_date_time(datetime(2026, 9, 24, 12, 34, 56))

    assert facade.get_formatted("%Y-%m-%d") == "2026-09-24"


def test_history_accumulates_values_in_order() -> None:
    facade = make_facade()
    first = datetime(2026, 9, 24, 15, 30, 45)
    second = datetime(2026, 9, 25, 0, 0, 0)
    third = datetime(2026, 9, 26, 12, 0, 0)

    facade.set_date_time(first)
    facade.set_date_time(second)
    facade.set_date_time(third)

    assert facade.get_history() == (first, second, third)


def test_reads_do_not_extend_history() -> None:
    facade = make_facade()
    value = datetime(2026, 9, 24, 15, 30, 45)
    facade.set_date_time(value)

    facade.get_date_time()
    facade.get_date_time()
    facade.get_formatted()

    assert facade.get_history() == (value,)


def test_history_is_immutable_outside() -> None:
    facade = make_facade()
    value = datetime(2026, 9, 24, 15, 30, 45)
    facade.set_date_time(value)
    history = facade.get_history()

    with pytest.raises(TypeError):
        history[0] = datetime(2027, 1, 1, 0, 0, 0)  # type: ignore[index]

    assert facade.get_history() == (value,)
