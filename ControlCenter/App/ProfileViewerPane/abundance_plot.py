from typing import Optional
from PySide6.QtCore import Signal, Slot
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QPushButton, QVBoxLayout
import numpy as np

from Server.Client.server_client import ServerClient
from .matplotlib_widget import MatplotlibWidget
from matplotlib.lines import Line2D


class AbundancePlot(MatplotlibWidget):
    selected_depth = Signal(float)

    def  __init__(self, client: ServerClient):
        super().__init__()

        self.server_client = client

        self.ax = self.figure.add_subplot(111)
        self.figure.canvas.mpl_connect("button_press_event", self.onclick)

        self.bin_size = 0.1
        self.depth_marker: Optional[Line2D] = None

    def update_plot(self):
        request = self.server_client.get_request(self.server_client.get_url() + 
            "/get-hdf-file-abundance")
        request.finished.connect(self._update_plot)

    @Slot()
    def _update_plot(self):
        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        data = self.server_client.get_data_from_reply(reply)["data"]
        reply.deleteLater()


        pressures: list[float] = data["pressures"]
        areas: list[list[float]] = data["areas"]

        binned_areas = [[]]
        current_bin = pressures[0]
        bins = [current_bin]
        for i, p in enumerate(pressures):
            # make new bin, assume pressures are sorted
            if p - current_bin > self.bin_size:  
                current_bin = p
                binned_areas.append([])
                bins.append(current_bin)

            binned_areas[-1].extend(areas[i])


        size_filtered = [[a for a in b if a > 500 and a < 1000] for b in binned_areas]
        abundance = [len(d) for d in size_filtered]

        size_filtered = [[a for a in b if a > 1000] for b in binned_areas]
        abundance_filtered = [len(d) for d in size_filtered]


        self.ax.clear()
        self.ax.set_ylabel("binned depth [dbar]")
        self.ax.set_xlabel("LPM Abundance")
        self.ax.plot(abundance_filtered, bins, label=">1000")
        self.ax.plot(abundance, bins, label="500-1000")
        self.ax.set_xmargin(0)
        self.ax.set_ymargin(0)
        self.ax.invert_yaxis()
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()


    def set_selected_depth(self, depth):
        depth = round(depth / self.bin_size) * self.bin_size
        x0, x1 = self.ax.get_xlim()
        if not self.depth_marker is None:
            self.depth_marker.set_data([x0, x1], [depth, depth])
        else:
            self.depth_marker, = self.ax.plot([x0, x1], [depth, depth], linestyle="--")
        self.ax.set_xlim(x0, x1)
        self.canvas.draw()

    def onclick(self, event):
        if event.inaxes is None:
            return
        y = event.ydata
        # round to nearest bin:
        y = round(y / self.bin_size) * self.bin_size
        self.selected_depth.emit(y)

    # def onclick(self, event):
    #     if event.inaxes is None:
    #         return
    #     y = event.ydata
    #     # round to nearest bin:
    #     y = round(y / self.bin_size) * self.bin_size
    #     x0, x1 = self.ax.get_xlim()
    #     if not self.depth_marker is None:
    #         self.depth_marker.set_data([x0, x1], [y, y])
    #     else:
    #         self.depth_marker, = self.ax.plot([x0, x1], [y, y], linestyle="--")
    #     self.selected_depth.emit(y)
    #     self.ax.set_xlim(x0, x1)
    #     self.canvas.draw()
