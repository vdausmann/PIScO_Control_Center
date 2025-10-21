# from App.HDF5ViewerPane.crops_to_hdf import generate_crop_hdf_file
#
#
# generate_crop_hdf_file(
#         "/home/tim/Documents/Arbeit/HDF5Test/SO298_298-10-1_PISCO2_20230422-2334_Results/Crops/",
#         "/home/tim/Documents/Arbeit/HDF5Test/SO298_298-10-1_PISCO2_20230422-2334_Results/Data/",
#         "/home/tim/Documents/Arbeit/HDF5Test/test.h5",
#         )

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import numpy as np
import matplotlib

matplotlib.use("QtAgg")


class MplWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        # Connect custom interactions
        self.mpl_connect("scroll_event", self.on_scroll)
        self.mpl_connect("pick_event", self.on_pick)

        self.plot_example()

    def plot_example(self):
        self.ax.clear()
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        self.ax.plot(x, y1, label="sin(x)", picker=True)
        self.ax.plot(x, y2, label="cos(x)", picker=True)
        self.ax.legend()
        self.draw()

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is None:
            return

        scale_factor = 1.2 if event.button == 'down' else 1 / 1.2
        xdata, ydata = event.xdata, event.ydata
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        new_width = (xlim[1] - xlim[0]) * scale_factor
        new_height = (ylim[1] - ylim[0]) * scale_factor
        relx = (xdata - xlim[0]) / (xlim[1] - xlim[0])
        rely = (ydata - ylim[0]) / (ylim[1] - ylim[0])

        ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
        ax.set_ylim([ydata - new_height * rely, ydata + new_height * (1 - rely)])
        self.draw_idle()

    def on_pick(self, event):
        artist = event.artist
        if event.mouseevent.button == 1 and isinstance(artist, Line2D):
            # Example: emphasize clicked line
            for line in self.ax.get_lines():
                line.set_linewidth(1)
            artist.set_linewidth(4)
            self.draw_idle()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Matplotlib in PySide6")

        self.plot_widget = MplWidget(self)
        self.toolbar = NavigationToolbar(self.plot_widget, self)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.plot_widget)
        self.setCentralWidget(central)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    app.exec()
