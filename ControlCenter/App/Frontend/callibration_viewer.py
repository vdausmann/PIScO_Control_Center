from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class CallibrationViewer(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.init_ui()


    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # view = QWebEngineView()
        # view.load(QUrl("https://www.geomar.de"))
        # view.resize(1024, 750)
        # view.show()
        # main_layout.addWidget(view)


