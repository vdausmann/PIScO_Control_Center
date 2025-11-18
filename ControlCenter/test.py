import sys
import traceback
from PySide6.QtWidgets import (
    QApplication, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


# ------------------ Matplotlib Canvas ------------------

class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def execute_script(self, script: str):
        """Run user script in a controlled environment."""
        try:
            # clear old plot
            self.fig.clear()
            ax = self.fig.add_subplot(111)

            # define execution environment
            env = {
                "fig": self.fig,
                "ax": ax,
            }

            exec(script, env)

            self.draw()
        except Exception as e:
            traceback.print_exc()


# ------------------ Recursive Split Widget ------------------

class PlotSplitWidget(QWidget):
    """A widget allowing recursive horizontal/vertical splits with matplotlib plots."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # toolbar with split buttons
        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

        btn_vsplit = QPushButton("Add Vertical Split")
        btn_hsplit = QPushButton("Add Horizontal Split")
        btn_load = QPushButton("Load Script")
        toolbar.addWidget(btn_vsplit)
        toolbar.addWidget(btn_hsplit)
        toolbar.addWidget(btn_load)

        # root content (initially a single plot)
        self.root = MatplotlibCanvas()
        self.container = self.root

        layout.addWidget(self.root)

        btn_vsplit.clicked.connect(lambda: self.split(Qt.Vertical))
        btn_hsplit.clicked.connect(lambda: self.split(Qt.Horizontal))
        btn_load.clicked.connect(self.load_script)

    def split(self, orientation):
        """Replace the current root widget with a splitter containing two plots."""
        # create splitter
        new_splitter = QSplitter(orientation)

        # old content
        old = self.container
        old.setParent(None)

        # new content
        new_canvas = MatplotlibCanvas()

        new_splitter.addWidget(old)
        new_splitter.addWidget(new_canvas)

        layout = self.layout()
        layout.replaceWidget(old, new_splitter)

        self.container = new_splitter

    def load_script(self):
        """Load and execute a user-provided Python script on all plots."""
        path, _ = QFileDialog.getOpenFileName(self, "Select Plot Script", "", "Python Files (*.py)")
        if not path:
            return

        with open(path, "r") as f:
            script = f.read()

        # apply script to all canvases recursively
        self._apply_to_canvases(self.container, script)

    def _apply_to_canvases(self, widget, script):
        """Recursively apply script to all Matplotlib canvases."""
        if isinstance(widget, MatplotlibCanvas):
            widget.execute_script(script)
            return

        if isinstance(widget, QSplitter):
            for i in range(widget.count()):
                child = widget.widget(i)
                self._apply_to_canvases(child, script)


# ------------------ Test Application ------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = PlotSplitWidget()
    w.resize(1200, 800)
    w.show()

    sys.exit(app.exec())
