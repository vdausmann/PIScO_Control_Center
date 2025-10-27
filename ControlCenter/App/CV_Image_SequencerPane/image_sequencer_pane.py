from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from dependencies.CV_Image_Sequencer.CV_Image_Sequencer_Lib import CVImageSequencerWidget
from dependencies.CV_Image_Sequencer.CV_Image_Sequencer_Lib.assets.styles.style import LIGHT, STYLE, DARK


class ImageSequencer(QWidget):

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        for key in LIGHT:
            STYLE[key] = LIGHT[key]

        widget = CVImageSequencerWidget(self.app)
        layout.addWidget(widget)

