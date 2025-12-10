from typing import Optional
from PySide6.QtCore import Signal, Slot
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QPushButton, QVBoxLayout
import numpy as np

from Server.Client.server_client import ServerClient
from .matplotlib_widget import MatplotlibWidget
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1 import make_axes_locatable


class CTDPlot(MatplotlibWidget):
    selected_depth = Signal(float)

    def  __init__(self, client: ServerClient):
        super().__init__()

        self.server_client = client

        update_button = QPushButton("Update Plot")
        update_button.clicked.connect(self.update_plot)
        self.main_layout.addWidget(update_button)

        self.ax = self.figure.add_subplot(111)
        self.divider = make_axes_locatable(self.ax)
        self.figure.canvas.mpl_connect("button_press_event", self.onclick)

        self.bin_size = 0.1
        self.depth_marker: Optional[Line2D] = None

    def update_plot(self):
        request = self.server_client.get_request(self.server_client.get_url() + 
            "/get-attributes-all-images")
        request.finished.connect(self._update_plot)

    @Slot()
    def _update_plot(self):
        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        data = self.server_client.get_data_from_reply(reply)["data"]
        reply.deleteLater()


        pressure: list[float] = data["pressure"]
        salinity = data["interpolated_s"]
        temperature = data["interpolated_t"]
        oxygen = data["interpolated_o"]
        chl = data["interpolated_chl"]

        self.ax.clear()

        ax_top1 = self.ax.twiny()
        ax_top2 = self.ax.twiny()
        ax_bottom1 = self.ax.twiny()
        ax_bottom2 = self.ax.twiny()

        ax_top1.spines["top"].set_position(("axes", 1.08))   # a bit above default
        ax_top2.spines["top"].set_position(("axes", 1.16))   # further above
        ax_bottom1.spines["top"].set_position(("axes", -0.08))  # below default
        ax_bottom2.spines["top"].set_position(("axes", -0.16))  # further below

        ax_top1.spines["top"].set_color("blue")
        ax_top2.spines["top"].set_color("green")
        ax_bottom1.spines["top"].set_color("red")
        ax_bottom2.spines["top"].set_color("cyan")

        ax_top1.set_xlabel("Temperature")
        ax_top2.set_xlabel("Oxygen")
        ax_bottom1.set_xlabel("Salinity")
        ax_bottom2.set_xlabel("CHL")


        self.ax.set_ylabel("binned depth [dbar]")

        temp, = ax_top1.plot(temperature, pressure, ".", label="temperature", color="blue",
                             zorder=0)
        oxygen, = ax_top2.plot(oxygen, pressure, ".", label="oxygen", color="green", zorder=0)
        salinity, = ax_bottom1.plot(salinity, pressure, ".", label="salinity", color="red",
                                    zorder=0)
        chl, = ax_bottom2.plot(chl, pressure, ".", label="chl", color="cyan", zorder=0)

        self.ax.set_xticks([])
        self.ax.grid(True)

        self.ax.legend([temp, oxygen, salinity, chl], ["Temperature", "Oxygen",
                                                       "Salinity", "CHL"])
        self.canvas.draw()

    def onclick(self, event):
        if event.inaxes is None:
            return
        y = event.ydata
        # round to nearest bin:
        y = round(y / self.bin_size) * self.bin_size
        x0, x1 = self.ax.get_xlim()
        if not self.depth_marker is None:
            self.depth_marker.set_data([x0, x1], [y, y])
        else:
            self.depth_marker, = self.ax.plot([x0, x1], [y, y], linestyle="--")
        self.selected_depth.emit(y)
        self.ax.set_xlim(x0, x1)
        self.canvas.draw()

