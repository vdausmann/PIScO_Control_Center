from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint

class PopupNotification(QWidget):
    def __init__(self, parent, message, manager, duration=5000):
        super().__init__(parent)
        self.manager = manager
        self.duration = duration

        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.adjustSize()

        QTimer.singleShot(duration, self.close_and_notify)

    def close_and_notify(self):
        self.manager.remove_notification(self)
        self.close()

class NotificationManager:
    def __init__(self, parent):
        self.parent = parent
        self.notifications: list[PopupNotification] = []

    def show_notification(self, message, duration=5000):
        popup = PopupNotification(self.parent, message, self, duration)
        self.notifications.append(popup)
        self._reposition_notifications()
        # self._position_notification(popup)
        popup.show()

    def remove_notification(self, popup):
        if popup in self.notifications:
            self.notifications.remove(popup)
            self._reposition_notifications()

    def _position_notification(self, popup):
        x_margin = 20
        y_margin = 20
        spacing = 10
        if not self.parent:
            return
        parent_rect = self.parent.geometry()
        x = parent_rect.x() + parent_rect.width() - x_margin

        current_y = parent_rect.y() + y_margin
        for other_popup in self.notifications:
            current_y += other_popup.height() + spacing
        popup.move(x - popup.width(), current_y)

    def _reposition_notifications(self):
        x_margin = 20
        y_margin = 20
        spacing = 10
        if not self.parent:
            return
        parent_rect = self.parent.geometry()
        x = parent_rect.x() + parent_rect.width() - x_margin

        current_y = parent_rect.y() + y_margin
        for popup in self.notifications:
            popup.hide()
            popup.move(x - popup.width(), current_y)
            popup.show()
            current_y += popup.height() + spacing

# class PopupNotification(QWidget):
#     def __init__(self, parent, message, manager, duration=5000):
#         super().__init__(parent)
#         self.manager = manager
#         self.duration = duration
#
#         self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #333;
#                 color: white;
#                 border-radius: 8px;
#                 padding: 10px;
#                 font-size: 14px;
#             }
#         """)
#
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         label = QLabel(message)
#         label.setWordWrap(True)
#         layout.addWidget(label)
#
#         self.adjustSize()
#
#         QTimer.singleShot(duration, self.close_and_notify)
#
#     def close_and_notify(self):
#         self.manager.remove_notification(self)
#         self.close()
