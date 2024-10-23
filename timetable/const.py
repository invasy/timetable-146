from pytz import timezone

TZ = timezone("Asia/Yekaterinburg")

DOW = [
    "понедельник",
    "вторник",
    "среду",
    "четверг",
    "пятницу",
    "субботу",
    "воскресенье",
]

_START = (9, 30), (9, 00), (8, 30)
_BREAKS = (10, 20, 20, 10, 10, 10), (10, 10, 20, 20, 10, 10)

DURATION = 45
START = tuple(_START[i] for i in (0, 1, 1, 0, 1, 2))
BREAKS = tuple(_BREAKS[i] for i in (0, 1, 1, 0, 1, 1))
