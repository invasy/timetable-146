from abc import ABCMeta, abstractmethod
from bisect import bisect, insort
from dataclasses import dataclass
from datetime import datetime, time, tzinfo
from functools import total_ordering
from typing import NoReturn, Self, Sequence

from .const import BREAKS, DOW, DURATION, START, TZ


@total_ordering
class Time:
    @classmethod
    def from_time(cls, t: time) -> Self:
        return cls(t.hour, t.minute)

    def __init__(self, hour: int | None = None, minute: int | None = None) -> None:
        self._time = 0
        if hour:
            self._time += hour * 60
        if minute:
            self._time += minute

    @property
    def hour(self) -> int:
        return (self._time // 60) % 24

    @property
    def minute(self) -> int:
        return self._time % 60

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.hour}, {self.minute})"

    def __str__(self) -> str:
        return f"{self.hour:2}:{self.minute:02}"

    def __add__(self, minutes: int) -> Self:
        if not isinstance(minutes, int):
            return NotImplemented
        return self.__class__(minute=self._time + minutes)

    def __sub__(self, other: "Time") -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(minute=self._time - other._time)

    def __eq__(self, other: "Time") -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._time == other._time

    def __lt__(self, other: "Time") -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._time < other._time


@dataclass(order=True)
class Period(metaclass=ABCMeta):
    start: Time
    duration: int = 0

    @abstractmethod
    def __str__(self) -> str:
        ...

    @property
    def time(self) -> str:
        return f"{self.start}—{self.start + self.duration}"


@dataclass(order=True)
class Lesson(Period):
    n: int = 0

    def __str__(self) -> str:
        return f"{self.n} урок"


@dataclass(order=True)
class Break(Period):
    def __str__(self) -> str:
        return f"Перемена ({self.duration} минут)"


@dataclass(order=True)
class End(Period):
    def __str__(self) -> str:
        return f"Завершение учебного дня"


class DayTimetable:
    def __init__(self, day: int) -> None:
        self.day = day
        self.timetable: Sequence[Period] = []

    def __str__(self) -> str:
        return f"Расписание звонков на {DOW[self.day]}:\n" \
            + "\n".join(f"{p.time} {p}" for p in self.timetable)

    def __len__(self) -> int:
        return len(self.timetable)

    def __validate_time(self, t: Time) -> NoReturn:
        if not isinstance(t, Time):
            raise TypeError
        if not self.timetable:
            raise ValueError("Сегодня нет уроков")
        first, last = self.timetable[0], self.timetable[-1]
        if t < first.start:
            raise ValueError("Уроки ещё не начались")
        if t > last.start + last.duration:
            raise ValueError("Уроки уже закончились")

    def __getitem__(self, t: Time) -> Period:
        self.__validate_time(t)
        return self.timetable[self.index(t)]

    def index(self, t: Time) -> int:
        return bisect(self.timetable, t, key=lambda p: p.start) - 1

    def next(self, t: Time) -> Period:
        self.__validate_time(t)
        return self.timetable[self.index(t) + 1]

    def append(self, period: Period) -> None:
        if not isinstance(period, Period):
            raise TypeError
        self.timetable.append(period)

    def insert(self, period: Period) -> None:
        if not isinstance(period, Period):
            raise TypeError
        insort(self.timetable, period)


START = tuple(Time(*t) for t in START)


class Timetable:
    def __init__(
        self,
        start_times: Sequence[Time] = START,
        lesson_duration: int = DURATION,
        breaks_durations: Sequence[Sequence[int]] = BREAKS,
        tz: tzinfo = TZ,
    ) -> None:
        self.timetable: Sequence[DayTimetable] = []
        for day in range(6):
            t = start_times[day]
            breaks = breaks_durations[day]
            timetable = DayTimetable(day)
            for i in range(7):
                timetable.append(Lesson(t, lesson_duration, i + 1))
                t += lesson_duration
                if i < len(breaks):
                    timetable.append(Break(t, breaks[i]))
                    t += breaks[i]
            self.timetable.append(timetable)
        self.timetable.append(DayTimetable(6))
        self.tz = tz

    def __getitem__(self, dow: int) -> DayTimetable:
        if not isinstance(dow, int):
            raise TypeError
        if dow < 0 or dow > 5:
            raise IndexError(dow)
        return self.timetable[dow]

    @property
    def _datetime(self) -> datetime:
        return datetime.now(tz=self.tz)

    @property
    def _dow(self) -> int:
        return self._datetime.date().weekday()

    @property
    def time(self) -> Time:
        t = self._datetime.time().replace(hour=9)
        return Time.from_time(t)

    @property
    def today(self) -> DayTimetable:
        return self[self._dow]

    @property
    def now(self) -> Period:
        return self.today[self.time]

    @property
    def next(self) -> Period:
        return self.today.next(self.time)

    @property
    def left(self) -> Time:
        return self.next.start - self.time

    def show(self, t: Time | None = None) -> str:
        t = t or self.time
        now = self.today[t]
        try:
            next = self.today.next(t)
        except IndexError:
            next = End(now.start + now.duration)
        return (
            f"{t} {now}\n"
            f"{next.start} ({next.start - t}) {next}"
        )
