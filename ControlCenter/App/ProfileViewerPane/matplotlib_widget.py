import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a Matplotlib Figure
        self.figure = Figure(layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create a layout and add toolbar + canvas
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addWidget(self.toolbar)

    #     # Add initial plot
    #     self.ax = self.figure.add_subplot(111)
    #     self.x_vals = np.linspace(0, 10, 200)
    #     self.y_vals = np.sin(self.x_vals)
    #     self.line, = self.ax.plot(self.x_vals, self.y_vals, picker=5)
    #     self.canvas.mpl_connect("pick_event", self.on_pick)
    #     self.canvas.draw()
    #
    # def on_pick(self, event):
    #     ind = event.ind[0]   # index of picked point
    #     x = self.x_vals[ind]
    #     y = self.y_vals[ind]
    #     print(f"Picked point: ({x:.3f}, {y:.3f})")
    #
    #     # Optionally highlight the selected point
    #     self.ax.plot(x, y, "ro", markersize=10)
    #     self.canvas.draw()
