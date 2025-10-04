from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen


class ClickableLabel(QLabel):
    clicked_signal = Signal()

    def __init__(self, text: str = "", width: int | None = None, height: int | None = None):
        super().__init__()
        self._text = text
        self._width = width
        self._height = height
        self.init_ui()

    def init_ui(self):
        self.setText(self._text)
        self.setObjectName("TaskWidget")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if self._width is not None:
            self.setFixedWidth(self._width)
        if self._height is not None:
            self.setFixedHeight(self._height)

    def mousePressEvent(self, ev):
        self.clicked_signal.emit()

    def clicked(self, clicked: bool):
        if clicked:
            self.setObjectName("TaskWidgetClicked")
        else:
            self.setObjectName("TaskWidget")


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


class SelectAllLineEdit(QLineEdit):
    def mouseDoubleClickEvent(self, arg__1) -> None:
        self.selectAll()

class LabelEntry(QWidget):

    def __init__(self, label: str = "Label is accessable via .label",
                 entry_text: str = "LineEdit is accessable via .entry",
                 parent = None, label_ratio: int = 1, entry_ratio: int = 1,
                 label_class = QLabel, entry_class = QLineEdit) -> None:
        super().__init__(parent)
        self.label_text = label
        self.entry_text = entry_text

        self.label = label_class()
        self.entry = entry_class()

        self.init_ui(label_ratio, entry_ratio, label_class, entry_class)

    def init_ui(self, label_ratio, entry_ratio, label_class, entry_class):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.label = label_class(self.label_text)
        self.entry = entry_class(self.entry_text)

        layout.addWidget(self.label, label_ratio)
        layout.addWidget(self.entry, entry_ratio)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0) # Take from index 0 repeatedly
        if item.widget():
            widget = item.widget()
            widget.setParent(None) 
            widget.deleteLater()  
        del item

def replace_widget(layout: QHBoxLayout | QVBoxLayout, old_widget: QWidget, new_widget: QWidget):
    # Find index of the old widget in the layout
    for i in range(layout.count()):
        if layout.itemAt(i).widget() is old_widget:
            # Remove the old widget
            layout.removeWidget(old_widget)
            old_widget.setParent(None)  # optional, fully detaches it

            # Insert the new widget at the same index
            layout.insertWidget(i, new_widget)
            return
