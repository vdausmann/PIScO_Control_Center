import sys
import json

from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
)
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QApplication


class ApiClient(QObject):
    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager(self)

    # ---- HTTP GET --------------------------------------------------------
    def get(self, url: str) -> QNetworkReply:
        req = QNetworkRequest(QUrl(url))
        reply = self.manager.get(req)
        return reply

    # ---- HTTP POST -------------------------------------------------------
    def post(self, url: str, payload: dict) -> QNetworkReply:
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        data = json.dumps(payload).encode("utf-8")
        reply = self.manager.post(req, data)
        return reply


class WebSocketClient(QObject):
    def __init__(self):
        super().__init__()
        self.ws = QWebSocket()

        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.errorOccurred.connect(self.on_error)

    def connect(self, url: str):
        self.ws.open(QUrl(url))

    @Slot()
    def on_connected(self):
        print("[WS] Connected")
        self.ws.sendTextMessage("Hello Server!")

    @Slot()
    def on_disconnected(self):
        print("[WS] Disconnected")

    @Slot()
    def on_message(self, msg):
        print("[WS] Message:", msg)

    @Slot()
    def on_error(self, error):
        print("[WS] Error:", error, self.ws.errorString())


class Tester(QObject):
    def __init__(self):
        super().__init__()
        self.api = ApiClient()
        self.ws = WebSocketClient()

        # ---- Test GET request --------------------------------------------
        reply = self.api.get("http://127.0.0.1:8000/test")
        reply.finished.connect(lambda r=reply: self.handle_reply(r))

        # ---- Test POST request -------------------------------------------
        reply2 = self.api.post(
            "http://127.0.0.1:8000/echo",
            {"message": "Hello from Qt!"}
        )
        reply2.finished.connect(lambda r=reply2: self.handle_reply(r))

        # ---- Test WebSocket ----------------------------------------------
        self.ws.connect("ws://127.0.0.1:8000/ws")

    @Slot()
    def handle_reply(self, reply: QNetworkReply):
        if reply.error() != QNetworkReply.NoError:
            print("[HTTP] Error:", reply.errorString())
        else:
            data = reply.readAll().data().decode("utf-8")
            print("[HTTP] Response:", data)

        reply.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tester = Tester()
    sys.exit(app.exec())
