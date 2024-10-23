import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget

from .timetable import Period, Timetable

LABELS = (
    ("Сейчас", "12:34", "1 урок"),
    ("Осталось", "00:00", None),
    ("Далее", "12:34", "Перемена (10 минут)"),
)


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        font = QFont(("Consolas", "monospace"), 16)
        bold = QFont(("Consolas", "monospace"), 16, QFont.Weight.Bold)
        widget = QWidget(self)
        grid = QGridLayout(widget)
        widget.setLayout(grid)

        self.setWindowTitle("Расписание звонков 146")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setCentralWidget(widget)
        self.labels: list[list[QLabel]] = []
        self.timetable = Timetable()

        for row, labels in enumerate(LABELS):
            r = []
            for col, label in enumerate(labels):
                if label is None:
                    continue
                l = QLabel(self)
                l.setFont(font)
                if label:
                    l.setText(label)
                grid.addWidget(l, row, col)
                r.append(l)
            self.labels.append(r)

        for row in range(3):
            label: QLabel = self.labels[row][1]
            label.setFont(bold)
            label.setFixedWidth(100)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

    def showTime(self) -> None:
        now, next = "", ""
        try:
            now = self.timetable.now
            next = self.timetable.next
            left = self.timetable.left
        except IndexError:
            now = "Сегодня нет уроков"
        except ValueError as ex:
            now = ex
        self.labels[0][1].setText(f"{now.start}" if isinstance(now, Period) else "")
        self.labels[0][2].setText(f"{now}")
        self.labels[1][1].setText(f"{left}" if next else "")
        self.labels[2][1].setText(f"{next.start}" if isinstance(next, Period) else "")
        self.labels[2][2].setText(f"{next}")


def main() -> int:
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    return app.exec()
