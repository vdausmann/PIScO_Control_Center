from typing import Optional
from PySide6.QtWidgets import (
        QCheckBox, QHeaderView, QLineEdit, QStackedWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QTreeWidget,
        QTreeWidgetItem, QHBoxLayout, QSplitter
)
import json
from PySide6.QtCore import QModelIndex, QObject, Qt, Signal, Slot, QThread
from PySide6.QtGui import QIntValidator

from PySide6.QtCore import Qt
from ..helper import HTTPErrorBox
from Server.Client.remote_hdf_file import RemoteHDFFile
from Server.Client.server_client import ServerClient


class Worker(QObject):
    finished = Signal(str)
    progress = Signal(int)

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        ...

class HDF5Viewer(QWidget):
    def __init__(self, server_client: ServerClient):
        super().__init__()

        self.server_client = server_client
        self.file: Optional[RemoteHDFFile] = None

        self.preload_groups = 10
        self.is_pisco_profile = True

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.file = None

        # Open file button
        self.open_btn = QPushButton("Open HDF5 File")
        self.open_btn.clicked.connect(self.open_file)
        layout.addWidget(self.open_btn)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        label = QLabel("Number of groups to load:")
        entry = QLineEdit(str(self.preload_groups))
        entry.setFixedWidth(100)
        entry.textChanged.connect(self.change_preload_groups)
        entry.setValidator(QIntValidator(bottom=-1))

        self.profile_checkbox = QCheckBox("HDF file of PISCO profile")
        self.profile_checkbox.setChecked(True)
        self.profile_checkbox.checkStateChanged.connect(self.change_pisco_check)

        row_layout.addWidget(label)
        row_layout.addWidget(entry)
        row_layout.addWidget(self.profile_checkbox)
        row_layout.addStretch()


        layout.addWidget(row)

        # Splitter for resizable layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)

        # --- Left: File tree ---
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Shape", "Dtype"])
        self.tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.tree)

        # --- Right: Vertical splitter for data + image ---
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(right_splitter)

        # Attributes:
        label = QLabel("Attributes", alignment=Qt.AlignmentFlag.AlignCenter)
        label.setFixedHeight(20)
        label.setStyleSheet("font-size: 16px;")
        self.attributes = QTextEdit()
        self.attributes.setReadOnly(True)
        right_splitter.addWidget(label)
        right_splitter.addWidget(self.attributes)

        # Data:
        self.data_space = QStackedWidget()

        label = QLabel("Data", alignment=Qt.AlignmentFlag.AlignCenter)
        label.setFixedHeight(20)
        label.setStyleSheet("font-size: 16px;")

        self.data = QTextEdit()
        self.data.setReadOnly(True)

        # self.image_label = QLabel()
        # self.image_label.setAlignment(Qt.AlignmentFlag.AlignLeft |
        #                               Qt.AlignmentFlag.AlignTop)
        # img_scroll_area = QScrollArea()
        # img_scroll_area.setWidget(self.image_label)

        
        self.data_space.addWidget(self.data)
        # self.data_space.addWidget(img_scroll_area)

        self.data_space.setCurrentIndex(0)

        right_splitter.addWidget(label)
        right_splitter.addWidget(self.data_space)
        right_splitter.setSizes([10, 100, 10, 200])

    @Slot()
    def change_preload_groups(self, text):
        try:
            self.preload_groups = int(text)
        except:
            pass

    @Slot()
    def change_pisco_check(self, check):
        self.is_pisco_profile = self.profile_checkbox.isChecked()
        print(self.is_pisco_profile)


    def open_file(self):
        if not self.file is None:
            self.file.close()
            self.file = None

        self.file = RemoteHDFFile(self.server_client, "/home/tim/Documents/Arbeit/PIScO_Control_Center/PISCO_Modules/FullSegmenter/Results/M181-165-1_CTD-048_00°00S-017°00W_20220508-0903.h5")
        code, detail = self.file.open()
        if code != 200:
            HTTPErrorBox(code, detail["detail"])
            return

        self.root_node = QTreeWidgetItem(["/", "Root", "-", "-"])
        self.root_node.setData(0, Qt.ItemDataRole.UserRole, ("group", "/"))
        self.tree.invisibleRootItem().addChild(self.root_node)

        # t = QThread()
        # t.start()
        self.populate_tree("/", self.root_node)
        self.root_node.setExpanded(True)


    def populate_tree(self, path: str, parent_item: QTreeWidgetItem):
        if self.file is None:
            return
        code, data = self.file.get_keys(path)
        if code != 200:
            HTTPErrorBox(code, data["detail"])
            return

        counter = 0
        for obj_name, obj_type in data.items():
            if obj_type == "group":
                node = QTreeWidgetItem([obj_name, "Group", "-", "-"])
                node.setData(0, Qt.ItemDataRole.UserRole, (obj_type, path + obj_name))
                parent_item.addChild(node)
                self.populate_tree(path + obj_name + "/", node)
            else:
                code, data = self.file.get_dataset_info(path + obj_name)
                if code != 200:
                    node = QTreeWidgetItem([obj_name, "Dataset", "NaN", "NaN"])
                else:
                    shape = data["shape"]
                    dtype = data["dtype"]
                    node = QTreeWidgetItem([obj_name, "Dataset", str(shape), dtype])
                parent_item.addChild(node)
                node.setData(0, Qt.ItemDataRole.UserRole, (obj_type, path + obj_name))
            counter += 1
            if counter >= self.preload_groups:
                break

        # self.tree.header().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)
        self.tree.header().setStretchLastSection(True)

        for column in [0, 1]:
            self.tree.setRootIndex(self.tree.model().index(0,0))
            self.tree.resizeColumnToContents(column)
            child_width = self.tree.columnWidth(column)

            self.tree.setRootIndex(QModelIndex())  # restore
            self.tree.setColumnWidth(column, child_width)


    def on_item_clicked(self, item, column):
        dtype, path = item.data(0, Qt.ItemDataRole.UserRole)
        if path is None:
            return
        if self.file is None:
            return

        code, attributes = self.file.get_attributes(path)
        if code != 200:
            self.attributes.setPlainText(f"Internal server error {code}: " +
                                         json.dumps(attributes, indent=4))
        self.attributes.setPlainText(json.dumps(attributes, indent=4))

        if dtype == "dataset":
            data = self.file[path]

            if self.is_pisco_profile and path.endswith("1D_crop_data"):
                group_path = "/".join(path.split("/")[:-1])
                width = self.file[group_path + "/width"]
                height = self.file[group_path + "/height"]
                # img = QPixmap.fromImage(convert_cv_to_qt(create_crop_collection_image(data,
                #                                           width, height, 400, len(width))))
                # label = QLabel()
                # label.setPixmap(img)
                # label.resize(img.size())
                # self.crop_flow_layout.addWidget(label)
                # self.data_space.setCurrentIndex(1)
            else:
                self.data.setPlainText(str(data))
        else:
            self.data_space.setCurrentIndex(0)
