from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QRgba64

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=50, line_width=5, color=QColor("#3498db")):
        super().__init__(parent)
        self._size = size
        self._line_width = line_width
        self._color = color
        self.setFixedSize(size, size)

        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        # self._timer.start(50)  # update every 50ms
        # self._timer.stop()


    def _rotate(self):
        self._angle = (self._angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(
            self._line_width, self._line_width, -self._line_width, -self._line_width
        )

        color = self._color if self._timer.isActive() else QColor(255, 0, 0, 1)
        pen = QPen(color, self._line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Draw an arc (270° of a circle)
        painter.drawArc(rect, int(self._angle * 16), 270 * 16)

    def toggle(self, on: bool | None = None):
        if on is None:
            if self._timer.isActive():
                self._timer.stop()
            else:
                self._timer.start(50)
        elif on and not self._timer.isActive():
            self._timer.start(50)
        elif not on and self._timer.isActive():
            self._timer.stop()

