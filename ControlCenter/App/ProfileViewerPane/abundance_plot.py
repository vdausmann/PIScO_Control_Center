from PySide6.QtCore import Slot
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QPushButton, QVBoxLayout
import numpy as np

from Server.Client.server_client import ServerClient
from .matplotlib_widget import MatplotlibWidget


class AbundancePlot(MatplotlibWidget):

    def  __init__(self, client: ServerClient):
        super().__init__()

        self.server_client = client

        update_button = QPushButton("Update Plot")
        update_button.clicked.connect(self.update_plot)
        self.main_layout.addWidget(update_button)

        self.ax = self.figure.add_subplot(111)

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

        bin_size = 0.1
        min_size = 1000

        pressures: list[float] = data["pressures"]
        areas: list[list[float]] = data["areas"]

        binned_areas = [[]]
        current_bin = pressures[0]
        bins = [current_bin]
        for i, p in enumerate(pressures):
            # make new bin, assume pressures are sorted
            if p - current_bin > bin_size:  
                current_bin = p
                binned_areas.append([])
                bins.append(current_bin)

            binned_areas[-1].extend(areas[i])


        size_filtered = [[a for a in b if a > min_size] for b in binned_areas]

        abundance = [len(d) for d in size_filtered]


        self.ax.plot(abundance, bins)
        self.canvas.draw()

        # rows = []
        # for p, area_list in zip(pressures, areas):
        #     for a in area_list:
        #         rows.append((p, a))
        # pressure_vs_area = np.array(rows)
        # print(pressure_vs_area.shape)
        #
