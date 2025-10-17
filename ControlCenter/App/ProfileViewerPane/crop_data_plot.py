import pyqtgraph as pg
import numpy as np





class CropDataPlot(pg.PlotWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Plot Example")

        # Create some example data
        self.x_data = np.linspace(0, 10, 10000)
        self.y_data = np.sin(self.x_data) + np.random.normal(0, 0.1, len(self.x_data))

        # Plot data
        self.curve = self.plot(self.x, self.y, pen=None, symbol='o', symbolSize=4, symbolBrush='y')

        # Highlighted point marker
        self.highlight = self.plot([], [], pen=None, symbol='o', symbolSize=10, symbolBrush='r')

        # Connect mouse click event
        self.scene().sigMouseClicked.connect(self.on_click)
