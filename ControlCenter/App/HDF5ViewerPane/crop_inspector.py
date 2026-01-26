from PySide6.QtWidgets import (QLayout, QScrollArea, QVBoxLayout, QWidget)
from PySide6.QtCore import QSize, QRect, QPoint
from PySide6.QtGui import QImage
import numpy as np
import cv2 as cv

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=8):
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        return self.itemList[index] if 0 <= index < len(self.itemList) else None

    def takeAt(self, index):
        return self.itemList.pop(index) if 0 <= index < len(self.itemList) else None

    def expandingDirections(self):
        return 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left()+margins.right(), margins.top()+margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX

            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class CropInspector(QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        self.flow_layout = FlowLayout(container)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

    def update_inspector(self):
        # self.flow_layout.addWidget(label)
        ...


def convert_cv_to_qt(image) -> QImage:
    if image.ndim == 2: # grayscale
        h, w = image.shape
        return QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
    elif image.shape[2] == 3:
        h, w, ch = image.shape
        rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    else:
        raise ValueError("Unsupported image format")

def create_crop_collection_image(pixel_values, widths, heights,
                                 max_width, n_crops):
    # first determine width and height of image:
    padding = 10
    max_w = max(max_width, np.max(widths[:n_crops]))
    max_h = 0
    h = 0
    w = 0
    for i in range(n_crops):
        if w + widths[i] > max_w:
            max_h += h + padding
            h = 0
            w = 0
        h = max(h, heights[i])
        w += widths[i] 

    max_h += h + padding
    img = np.ones((max_h, max_w), dtype=np.uint8) * 255

    offset = 0
    current_w = 0
    current_h = 0
    max_h = 0
    for i in range(n_crops):
        w = widths[i]
        h = heights[i]

        if current_w + w > max_w:
            current_h += max_h + padding
            max_h = 0
            current_w = 0
        max_h = max(h, max_h)

        data = np.array(pixel_values[offset:offset + w * h]).reshape(h, w)
        offset += w * h
        img[current_h:current_h + h, current_w:current_w + w] = data

        current_w += w

    return img
