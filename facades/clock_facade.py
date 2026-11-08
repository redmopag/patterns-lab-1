from datetime import datetime

from adapters import DigitalClockAdapter
from services import ClockFormatter, ClockHistory


class ClockFacade:
    def __init__(
        self,
        adapter: DigitalClockAdapter,
        formatter: ClockFormatter,
        history: ClockHistory,
    ) -> None:
        self._adapter = adapter
        self._formatter = formatter
        self._history = history

    def set_date_time(self, date: datetime) -> None:
        self._adapter.set_date_time(date)
        self._history.add(date)

    def get_date_time(self) -> datetime:
        return self._adapter.get_date_time()

    def get_formatted(self, fmt: str = "%d.%m.%Y %H:%M:%S") -> str:
        return self._formatter.format(self._adapter.get_date_time(), fmt)

    def get_history(self) -> tuple[datetime, ...]:
        return self._history.all()
