from typing import Optional
from PySide6.QtWidgets import (
        QGridLayout, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from .ctd_plot import CTDPlot

from .abundance_plot import AbundancePlot
from Server.Client.server_client import ServerClient
from .matplotlib_widget import MatplotlibWidget

class ProfileViewer(QWidget):
    def __init__(self, server_client: ServerClient):
        super().__init__()

        self.server_client = server_client
        self.depth_to_filename: Optional[dict] = None

        self.init_ui()


    def init_ui(self):
        main_layout = QVBoxLayout(self)

        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        label = QLabel("Select profile:")
        label.setStyleSheet("font-size: 22;")
        top_bar_layout.addWidget(label)


        main_layout.addWidget(top_bar, 1)


        plot_grid = QWidget()
        plot_grid_layout = QGridLayout(plot_grid)

        self.ctd = CTDPlot(self.server_client)
        self.ctd.selected_depth.connect(self.on_selected_depth)

        self.particle_distribution = AbundancePlot(self.server_client)
        self.particle_distribution.selected_depth.connect(self.on_selected_depth)

        full_img = MatplotlibWidget()

        crop = MatplotlibWidget()

        plot_grid_layout.addWidget(self.ctd, 0, 0, 2, 1)
        plot_grid_layout.addWidget(self.particle_distribution, 0, 1, 2, 1)

        plot_grid_layout.addWidget(full_img, 0, 2, 1, 1)
        plot_grid_layout.addWidget(crop, 1, 2, 1, 1)

        main_layout.addWidget(plot_grid, 20)

        update_button = QPushButton("Update Plots")
        update_button.clicked.connect(self.update_plots)
        main_layout.addWidget(update_button)

    @Slot(float)
    def on_selected_depth(self, depth: float):
        self.ctd.set_selected_depth(depth)
        self.particle_distribution.set_selected_depth(depth)

    def update_plots(self):
        request = self.server_client.get_request(self.server_client.get_url() + 
            "/get-depth-filename-dict")

        request = self.server_client.get_request(self.server_client.get_url() + 
            "/get-attributes-all-images")
        request.finished.connect(self.ctd._update_plot)

        request = self.server_client.get_request(self.server_client.get_url() + 
            "/get-hdf-file-abundance")
        request.finished.connect(self.particle_distribution._update_plot)
