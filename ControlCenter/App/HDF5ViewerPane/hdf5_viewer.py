from typing import Optional
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import (
        QLineEdit, QSizePolicy, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QTreeWidget,
        QTreeWidgetItem, QHBoxLayout, QSplitter
)
import numpy as np
import json
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QIntValidator, QPixmap
import cv2 

import h5py
from PySide6.QtCore import Qt
from Server.Client.file_explorer import ServerFileDialog
from Server.Client.server_client import ServerClient

class HDF5Viewer(QWidget):
    def __init__(self, server_client: ServerClient):
        super().__init__()

        self.server_client = server_client

        self.preload_groups = 10


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

        row_layout.addWidget(label)
        row_layout.addWidget(entry)
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

        # Text info
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        right_splitter.addWidget(self.text)

        # Image viewer
        self.image_label = QLabel("No image selected.")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)  # We will handle scaling manually
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._current_pixmap = None  # store the image for resizing
        right_splitter.addWidget(self.image_label)

    @Slot()
    def change_preload_groups(self, text):
        try:
            self.preload_groups = int(text)
        except:
            pass

    def open_file(self):
        # dialog = ServerFileDialog(self.server_client, "/home/tim/Documents/Arbeit/HDF5Test/")
        dialog = ServerFileDialog(self.server_client)
        if dialog.exec():
            path = dialog.selected_path()
            reply = self.server_client.open_hdf_file(path)
            reply.finished.connect(self._open_file)

    @Slot()
    def _open_file(self):
        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return
        reply.deleteLater()

        # get root
        reply = self.server_client.get_hdf_file_group_structure("/")
        reply.finished.connect(self.get_roots)
        self.tree.clear()


    @Slot()
    def get_roots(self):
        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        roots = self.server_client.get_data_from_reply(reply)["data"]
        reply.deleteLater()

        counter = 0 
        for root, _ in roots["members"].items():
            reply = self.server_client.get_hdf_file_full_structure("/" + root)
            reply.finished.connect(self.populate_tree)
            counter += 1

            if self.preload_groups >= 0 and counter >= self.preload_groups:
                break

    @Slot()
    def populate_tree(self):
        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        group = self.server_client.get_data_from_reply(reply)["data"]
        reply.deleteLater()

        root = list(group)[0]
        root_node = QTreeWidgetItem([root, "Group", "-", "-"])
        root_node.setData(0, Qt.ItemDataRole.UserRole, ("group", root))
        self.tree.invisibleRootItem().addChild(root_node)

        self._populate_tree(group[root], root_node)


    def _populate_tree(self, group, parent_item):
        for item_path, item in group.items():
            if item["type"] == "group":
                node = QTreeWidgetItem([item_path.split("/")[-1], "Group", "-", "-"])
                node.setData(0, Qt.ItemDataRole.UserRole, ("group", item_path))
                parent_item.addChild(node)
                self._populate_tree(item, node)
            elif item["type"] == "dataset":
                shape = str(item["shape"])
                dtype = str(item["dtype"])
                node = QTreeWidgetItem([item_path.split("/")[-1], "Dataset", shape, dtype])
                node.setData(0, Qt.ItemDataRole.UserRole, ("dataset", item_path))
                parent_item.addChild(node)

    # -------------------------------------------------------------------------

    def on_item_clicked(self, item, column):
        dtype, path = item.data(0, Qt.ItemDataRole.UserRole)
        if path is None:
            return

        if dtype == "group":
            reply = self.server_client.get_hdf_file_attributes(path)
            reply.finished.connect(self._show_data)
        else:
            reply = self.server_client.get_hdf_file_data(path)
            reply.finished.connect(self._show_data)

    @Slot(QNetworkReply)
    def _show_data(self):
        self.image_label.clear()

        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        result = self.server_client.get_data_from_reply(reply)
        data = result["data"]
        if "type" in data and data["type"] == "group":
            data.pop("structure")

        if type(data) == dict:
            self.text.setPlainText(json.dumps(data, indent=4))
        elif self.try_show_image(data):
            self.text.setPlainText("Displayed as image.")
        else:
            preview = self.array_preview(data)
            self.text.setPlainText(preview)

    @Slot(QNetworkReply)
    def _show_attributes(self):
        self.image_label.clear()

        reply = self.sender()
        if not isinstance(reply, QNetworkReply):
            return

        result = self.server_client.get_data_from_reply(reply)
        data = result["data"]
        if "type" in data and data["type"] == "group":
            data.pop("structure")

        if type(data) == dict:
            self.text.setPlainText(json.dumps(data, indent=4))
        elif self.try_show_image(data):
            self.text.setPlainText("Displayed as image.")
        else:
            preview = self.array_preview(data)
            self.text.setPlainText(preview)


    def set_image(self, qimg: QImage):
        """Display an image scaled to fit the current label width."""
        pixmap = QPixmap.fromImage(qimg)
        self._current_pixmap = pixmap
        self.update_scaled_image()

    def update_scaled_image(self):
        """Rescale current pixmap to fit the available width while keeping aspect ratio."""
        if not self._current_pixmap:
            return
        label_width = self.image_label.width()
        scaled = self._current_pixmap.scaledToWidth(label_width, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        """Re-scale image when user resizes the window/splitter."""
        super().resizeEvent(event)
        self.update_scaled_image()

    def try_show_image(self, data):
        """Try to show numpy array as an image, return True if successful."""
        if not isinstance(data, np.ndarray):
            return False

        # Grayscale
        if data.ndim == 2:
            img = self.normalize_to_uint8(data)
            qimg = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format_Grayscale8)
            self.set_image(qimg)
            return True

        # RGB
        if data.ndim == 3 and data.shape[2] in (3, 4):
            img = self.normalize_to_uint8(data)
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                qformat = QImage.Format_BGR888
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
                qformat = QImage.Format_BGRA8888
            qimg = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], qformat)
            self.set_image(qimg)
            return True

        return False

    # -------------------------------------------------------------------------
    def normalize_to_uint8(self, arr):
        """Convert arbitrary numeric array to uint8 image range [0,255]."""
        if np.issubdtype(arr.dtype, np.floating):
            arr = np.nan_to_num(arr)
            arr = (arr - arr.min()) / (arr.ptp() + 1e-8)
            arr = (arr * 255).astype(np.uint8)
        elif np.issubdtype(arr.dtype, np.integer):
            info = np.iinfo(arr.dtype)
            arr = ((arr - info.min) / (info.max - info.min) * 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        return arr

    # -------------------------------------------------------------------------
    def array_preview(self, arr):
        """Generate small textual preview of array content."""
        if np.isscalar(arr):
            return str(arr)
        if arr.ndim == 1 and arr.size < 200:
            return np.array2string(arr, threshold=100)
        if arr.ndim <= 2 and np.prod(arr.shape) < 400:
            return np.array2string(arr, threshold=100)
        return f"<Large dataset: shape={arr.shape}>"

    # -------------------------------------------------------------------------
    def closeEvent(self, event):
        if self.file:
            self.file.close()
        event.accept()
