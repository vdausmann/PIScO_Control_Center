from PySide6.QtWidgets import (
        QGridLayout, QHBoxLayout, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class ProfileViewer(QWidget):
    def __init__(self):
        super().__init__()
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

        physical_observables = QWidget()
        physical_observables.setStyleSheet("background-color: red;")

        particle_distribution = QWidget()
        particle_distribution.setStyleSheet("background-color: green;")

        full_img = QWidget()
        full_img.setStyleSheet("background-color: yellow;")

        crop = QWidget()
        crop.setStyleSheet("background-color: blue;")

        plot_grid_layout.addWidget(physical_observables, 0, 0, 2, 1)
        plot_grid_layout.addWidget(particle_distribution, 0, 1, 2, 1)

        plot_grid_layout.addWidget(full_img, 0, 2, 1, 1)
        plot_grid_layout.addWidget(crop, 1, 2, 1, 1)

        main_layout.addWidget(plot_grid, 20)



    def save_state(self, state: dict):
        ...

    def load_state(self, state: dict):
        ...
