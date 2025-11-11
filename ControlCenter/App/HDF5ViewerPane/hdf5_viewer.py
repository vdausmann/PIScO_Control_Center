from PySide6.QtWidgets import (
        QSizePolicy, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QTreeWidget,
        QTreeWidgetItem, QHBoxLayout, QSplitter
)
import numpy as np
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
import cv2 

import h5py
from PySide6.QtCore import Qt

class HDF5Viewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self._open_file("./test.h5")

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.file = None

        # Open file button
        self.open_btn = QPushButton("Open HDF5 File")
        self.open_btn.clicked.connect(self.open_file)
        layout.addWidget(self.open_btn)

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

    # -------------------------------------------------------------------------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open HDF5 File", "", "HDF5 Files (*.h5 *.hdf5)")
        self._open_file(path)

    def _open_file(self, path: str):
        if not path:
            return
        if self.file:
            self.file.close()

        self.file = h5py.File(path, "r")
        self.tree.clear()
        self.populate_tree(self.file, self.tree.invisibleRootItem(), "/")


    # -------------------------------------------------------------------------
    def populate_tree(self, group, parent_item, path):
        for key, item in group.items():
            item_path = f"{path}{key}" if path.endswith("/") else f"{path}/{key}"

            if isinstance(item, h5py.Group):
                node = QTreeWidgetItem([key, "Group", "-", "-"])
                parent_item.addChild(node)
                self.populate_tree(item, node, item_path)
            elif isinstance(item, h5py.Dataset):
                shape = str(item.shape)
                dtype = str(item.dtype)
                node = QTreeWidgetItem([key, "Dataset", shape, dtype])
                node.setData(0, Qt.ItemDataRole.UserRole, item_path)
                parent_item.addChild(node)

    # -------------------------------------------------------------------------

    def on_item_clicked(self, item, column):
        if not self.file:
            return

        path = item.data(0, Qt.ItemDataRole.UserRole)
        self.image_label.clear()

        if not path:
            self.text.setPlainText("Group selected.")
            return

        try:
            ds = self.file[path]
            if not isinstance(ds, h5py.Dataset):
                return
            info = f"Path: {path}\nShape: {ds.shape}\nDtype: {ds.dtype}\n\n"
            data = ds[()]

            # Decode bytes if necessary
            if isinstance(data, (bytes, np.bytes_)):
                data = data.decode('utf-8')
            # Try to parse JSON
            if isinstance(data, str):
                try:
                    json_data = json.loads(data)
                    formatted_json = json.dumps(json_data, indent=4)
                    self.text.setPlainText(info + formatted_json)
                    return
                except Exception:
                    pass  # Not valid JSON, fall back to plain text

            # Try to display as image
            if self.try_show_image(data):
                self.text.setPlainText(info + "Displayed as image.")
            else:
                preview = self.array_preview(data)
                self.text.setPlainText(info + preview)

        except Exception as e:
            self.text.setPlainText(f"Error reading dataset:\n{e}")

    # -------------------------------------------------------------------------
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
        # if type(arr) == bytes:
        #     data = json.loads(arr.decode())
        #     return data
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
