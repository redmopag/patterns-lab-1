from datetime import datetime

from adapters import DigitalClockAdapter
from clocks import AnalogClock
from facades import ClockFacade
from services import ClockFormatter, ClockHistory


def main() -> None:
    facade = ClockFacade(
        adapter=DigitalClockAdapter(AnalogClock()),
        formatter=ClockFormatter(),
        history=ClockHistory(),
    )

    facade.set_date_time(datetime(2026, 9, 24, 15, 30, 45))
    print(facade.get_formatted())

    facade.set_date_time(datetime(2026, 9, 25, 0, 0, 0))
    print(facade.get_formatted())
    print("История установленных значений:")
    for value in facade.get_history():
        print(f"  {value}")


if __name__ == "__main__":
    main()
