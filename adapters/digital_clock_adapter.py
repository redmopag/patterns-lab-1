from datetime import datetime, timedelta

from consts import DayNightDivision
from interfaces import BaseAnalogClock, BaseDigitalClock

HOUR_HAND_STEP = 30.0  # градусов на час: циферблат 360° / 12 часов
MINUTE_HAND_STEP = 6.0  # градусов на минуту: 360° / 60 минут
SECOND_HAND_STEP = 6.0  # градусов на секунду: 360° / 60 секунд
HALF_DAY_HOURS = 12  # размер 12-часового циферблата


class DigitalClockAdapter(BaseDigitalClock):

    def __init__(self, analog_clock: BaseAnalogClock) -> None:
        self._analog_clock = analog_clock

    def set_date_time(self, date: datetime) -> None:
        """Переводит `datetime` в дату, углы стрелок и признак AM/PM аналоговых часов.

        Модель дискретная: каждая стрелка стоит ровно на делении своей единицы
        времени - часовая по 30° на час, минутная и секундная по 6°.  
        Циферблат 12-часовой, поэтому полночь и полдень дают одну и ту же позицию стрелок
        (0°) и различаются только признаком AM/PM.  
        У модели секундная точность, поэтому микросекунды округляются до ближайшей секунды, 
        включая перенос в минуту, час и дату при переполнении.
        """
        rounded = self._round_to_second(date)
        division = (
            DayNightDivision.PM
            if rounded.hour >= HALF_DAY_HOURS
            else DayNightDivision.AM
        )
        self._analog_clock.set_date_time(
            year=rounded.year,
            month=rounded.month,
            day=rounded.day,
            hour_angle=(rounded.hour % HALF_DAY_HOURS) * HOUR_HAND_STEP,
            minute_angle=rounded.minute * MINUTE_HAND_STEP,
            second_angle=rounded.second * SECOND_HAND_STEP,
            day_night_division=division,
        )

    def get_date_time(self) -> datetime:
        """Собирает `datetime` из даты, углов стрелок и признака AM/PM аналоговых часов.

        Стрелки независимы, поэтому каждая единица времени читается прямо из
        своей стрелки: 
        - минута и секунда - угол / 6, 
        - час - угол / 30 (позиция на 12-часовом циферблате, 0–11). 
        
        Итоговый час 0–23 восстанавливается по признаку части суток:
        - AM оставляет часы как есть (полночь - «0° + AM» - это час 0), 
        - PM добавляет 12 (полдень - «0° + PM» - час 12).
        """
        hour_on_dial = (
            round(self._analog_clock.get_hour_angle() / HOUR_HAND_STEP) % HALF_DAY_HOURS
        )
        minute = round(self._analog_clock.get_minute_angle() / MINUTE_HAND_STEP) % 60
        second = round(self._analog_clock.get_second_angle() / SECOND_HAND_STEP) % 60
        if self._analog_clock.get_day_night_division() is DayNightDivision.PM:
            hour = hour_on_dial + HALF_DAY_HOURS
        else:
            hour = hour_on_dial
        return datetime(
            self._analog_clock.get_year(),
            self._analog_clock.get_month(),
            self._analog_clock.get_day(),
            hour,
            minute,
            second,
        )

    @staticmethod
    def _round_to_second(date: datetime) -> datetime:
        """Отбрасывает микросекунды с округлением до ближайшей секунды."""
        without_micro = date.replace(microsecond=0)
        if date.microsecond >= 500_000:
            return without_micro + timedelta(seconds=1)
        return without_micro
